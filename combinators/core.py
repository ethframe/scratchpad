from abc import abstractmethod
from dataclasses import dataclass
from itertools import chain
from typing import (
    Callable, Dict, Generic, Iterable, List, NoReturn, Optional, Sequence,
    Tuple, TypeVar, Union
)

T = TypeVar("T")
V = TypeVar("V", bound=object)
V_co = TypeVar("V_co", covariant=True)
U = TypeVar("U", bound=object)
X = TypeVar("X", bound=object)


@dataclass
class ErrorItem:
    pos: int
    expected: List[str]

    def msg(self) -> str:
        if not self.expected:
            return "at {}: unexpected input".format(self.pos)
        if len(self.expected) == 1:
            return "at {}: expected {}".format(self.pos, self.expected[0])
        return "at {}: expected {} or {}".format(
            self.pos, ', '.join(self.expected[:-1]), self.expected[-1]
        )


class ParseError(Exception):
    def __init__(self, errors: List[ErrorItem]):
        super().__init__(errors)
        self.errors = errors

    def __str__(self) -> str:
        return ", ".join(error.msg() for error in self.errors)


class RepairOp:
    pos: int
    expected: Iterable[str]


@dataclass
class Skip(RepairOp):
    count: int
    pos: int
    expected: Iterable[str] = ()


@dataclass
class Insert(RepairOp):
    token: str
    pos: int
    expected: Iterable[str] = ()


@dataclass
class Repair(Generic[V_co]):
    cost: int
    value: V_co
    pos: int
    ops: Iterable[RepairOp]


@dataclass
class Ok(Generic[V_co]):
    value: V_co
    pos: int
    expected: Iterable[str] = ()

    def unwrap(self, recover: bool = False) -> V_co:
        return self.value

    def fmap(self, fn: Callable[[V_co], U]) -> "Ok[U]":
        return Ok(fn(self.value), self.pos, self.expected)

    def expect(self, expected: Iterable[str]) -> "Ok[V_co]":
        return Ok(self.value, self.pos, expected)


@dataclass
class Error:
    pos: int
    expected: Iterable[str] = ()

    def unwrap(self, recover: bool = False) -> NoReturn:
        self.expected = list(self.expected)
        raise ParseError([ErrorItem(self.pos, self.expected)])

    def fmap(self, fn: object) -> "Error":
        return self

    def expect(self, expected: Iterable[str]) -> "Error":
        return Error(self.pos, expected)


@dataclass
class Recovered(Generic[V_co]):
    repairs: Iterable[Repair[V_co]]
    pos: int
    expected: Iterable[str] = ()

    def unwrap(self, recover: bool = False) -> V_co:
        self.repairs = list(self.repairs)
        repair = self.repairs[0]
        if recover:
            return repair.value
        errors: List[ErrorItem] = []
        repair.ops = list(repair.ops)
        for op in repair.ops:
            op.expected = list(op.expected)
            errors.append(ErrorItem(op.pos, op.expected))
        raise ParseError(errors)

    def fmap(self, fn: Callable[[V_co], U]) -> "Recovered[U]":
        return Recovered(
            [Repair(p.cost, fn(p.value), p.pos, p.ops) for p in self.repairs],
            self.pos, self.expected
        )

    def expect(self, expected: Iterable[str]) -> "Recovered[V_co]":
        return Recovered(self.repairs, self.pos, expected)


Result = Union[Recovered[V], Ok[V], Error]

ParseFn = Callable[[Sequence[T], int, int], Result[V]]


def merge_expected(pos: int, ra: Result[V], rb: Result[U]) -> Iterable[str]:
    if ra.pos != pos and ra.pos != rb.pos:
        return rb.expected
    return chain(ra.expected, rb.expected)


class Parser(Generic[T, V_co]):
    def parse(
            self, stream: Sequence[T], recover: bool = False) -> Result[V_co]:
        return self(stream, 0, -1 if recover else len(stream))

    @abstractmethod
    def __call__(self, stream: Sequence[T], pos: int, bt: int) -> Result[V_co]:
        ...

    def to_fn(self) -> ParseFn[T, V_co]:
        return self

    def fmap(self, fn: Callable[[V_co], U]) -> "Parser[T, U]":
        self_fn = self.to_fn()

        def fmap(stream: Sequence[T], pos: int, bt: int) -> Result[U]:
            return self_fn(stream, pos, bt).fmap(fn)

        return FnParser(fmap)

    def bind(self, fn: Callable[[V_co], "Parser[T, U]"]) -> "Parser[T, U]":
        self_fn = self.to_fn()

        def bind(stream: Sequence[T], pos: int, bt: int) -> Result[U]:
            ra = self_fn(stream, pos, bt)
            if isinstance(ra, Error):
                return ra
            if isinstance(ra, Recovered):
                return bind_recover(ra, stream)
            rb = fn(ra.value)(stream, ra.pos, bt)
            return rb.expect(merge_expected(pos, ra, rb))

        def bind_recover(
                ra: Recovered[V_co], stream: Sequence[T]) -> Result[U]:
            reps: Dict[int, Repair[U]] = {}
            for pa in ra.repairs:
                rb = fn(pa.value)(stream, pa.pos, -1)
                if isinstance(rb, Ok):
                    if rb.pos not in reps or pa.cost < reps[rb.pos].cost:
                        reps[rb.pos] = Repair(
                            pa.cost, rb.value, rb.pos, pa.ops)
                elif isinstance(rb, Recovered):
                    pa_ops = list(pa.ops)
                    for pb in rb.repairs:
                        cost = pa.cost + pb.cost
                        if pb.pos not in reps or cost < reps[pb.pos].cost:
                            reps[pb.pos] = Repair(
                                cost, pb.value, pb.pos, chain(pa_ops, pb.ops)
                            )
            if reps:
                return Recovered(list(reps.values()), ra.pos, ra.expected)
            return Error(ra.pos, ra.expected)

        return FnParser(bind)

    def lseq(self, other: "Parser[T, U]") -> "Parser[T, V_co]":
        return lseq(self, other)

    def rseq(self, other: "Parser[T, U]") -> "Parser[T, U]":
        return rseq(self, other)

    def __add__(self, other: "Parser[T, U]") -> "Parser[T, Tuple[V_co, U]]":
        return seq(self, other)

    def __or__(self, other: "Parser[T, V_co]") -> "Parser[T, V_co]":
        self_fn = self.to_fn()
        other_fn = other.to_fn()

        def or_(stream: Sequence[T], pos: int, bt: int) -> Result[V_co]:
            ra = self_fn(stream, pos, max(pos, bt))
            if ra.pos != pos:
                return ra
            rb = other_fn(stream, pos, max(pos, bt))
            if rb.pos != pos:
                return rb
            expected = chain(ra.expected, rb.expected)
            if isinstance(ra, Ok):
                return Ok(ra.value, pos, expected)
            if isinstance(rb, Ok):
                return Ok(rb.value, pos, expected)
            if pos > bt:
                ra = self_fn(stream, pos, -1)
                rb = other_fn(stream, pos, -1)
                if isinstance(ra, Recovered):
                    if isinstance(rb, Recovered):
                        reps = {pb.pos: pb for pb in rb.repairs}
                        reps.update((pa.pos, pa) for pa in ra.repairs)
                        return Recovered(list(reps.values()), ra.pos, expected)
                    return Recovered(ra.repairs, ra.pos, expected)
                if isinstance(rb, Recovered):
                    return Recovered(rb.repairs, ra.pos, expected)
            return Error(pos, expected)

        return FnParser(or_)

    def maybe(self) -> "Parser[T, Optional[V_co]]":
        return maybe(self)

    def many(self) -> "Parser[T, List[V_co]]":
        return many(self)

    def label(self, expected: str) -> "Parser[T, V_co]":
        return label(self, expected)

    def sep_by(self, sep: "Parser[T, U]") -> "Parser[T, List[V_co]]":
        return sep_by(self, sep)

    def between(
            self, open: "Parser[T, U]",
            close: "Parser[T, X]") -> "Parser[T, V_co]":
        return between(open, close, self)


class FnParser(Parser[T, V_co]):
    def __init__(self, fn: ParseFn[T, V_co]):
        self._fn = fn

    def to_fn(self) -> ParseFn[T, V_co]:
        return self._fn

    def __call__(self, stream: Sequence[T], pos: int, bt: int) -> Result[V_co]:
        return self._fn(stream, pos, bt)


def _make_seq(
        parser: Parser[T, V], second: Parser[T, U],
        fn: Callable[[V, U], X]) -> Parser[T, X]:
    parser_fn = parser.to_fn()
    second_fn = second.to_fn()

    def seq(stream: Sequence[T], pos: int, bt: int) -> Result[X]:
        ra = parser_fn(stream, pos, bt)
        if isinstance(ra, Error):
            return ra
        if isinstance(ra, Recovered):
            return seq_recover(ra, stream)
        va = ra.value
        rb = second_fn(stream, ra.pos, bt)
        return rb.fmap(lambda vb: fn(va, vb)).expect(
            merge_expected(pos, ra, rb)
        )

    def seq_recover(ra: Recovered[V], stream: Sequence[T]) -> Result[X]:
        reps: Dict[int, Repair[X]] = {}
        for pa in ra.repairs:
            rb = second_fn(stream, pa.pos, -1)
            if isinstance(rb, Ok):
                if rb.pos not in reps or pa.cost < reps[rb.pos].cost:
                    reps[rb.pos] = Repair(
                        pa.cost, fn(pa.value, rb.value), rb.pos, pa.ops
                    )
            elif isinstance(rb, Recovered):
                pa_ops = list(pa.ops)
                for pb in rb.repairs:
                    cost = pa.cost + pb.cost
                    if pb.pos not in reps or cost < reps[pb.pos].cost:
                        reps[pb.pos] = Repair(
                            cost, fn(pa.value, pb.value), pb.pos,
                            chain(pa_ops, pb.ops)
                        )
        if reps:
            return Recovered(list(reps.values()), ra.pos, ra.expected)
        return Error(ra.pos, ra.expected)

    return FnParser(seq)


def lseq(parser: Parser[T, V], second: Parser[T, U]) -> Parser[T, V]:
    return _make_seq(parser, second, lambda l, _: l)


def rseq(parser: Parser[T, V], second: Parser[T, U]) -> Parser[T, U]:
    return _make_seq(parser, second, lambda _, r: r)


def seq(parser: Parser[T, V], second: Parser[T, U]) -> Parser[T, Tuple[V, U]]:
    return _make_seq(parser, second, lambda l, r: (l, r))


class Pure(Parser[T, V_co]):
    def __init__(self, x: V_co):
        self._x = x

    def __call__(self, stream: Sequence[T], pos: int, bt: int) -> Result[V_co]:
        return Ok(self._x, pos)


pure = Pure


class PureFn(Parser[T, V_co]):
    def __init__(self, fn: Callable[[], V_co]):
        self._fn = fn

    def __call__(self, stream: Sequence[T], pos: int, bt: int) -> Result[V_co]:
        return Ok(self._fn(), pos)


pure_fn = PureFn


class Eof(Parser[T, None]):
    def __call__(self, stream: Sequence[T], pos: int, bt: int) -> Result[None]:
        if pos == len(stream):
            return Ok(None, pos)
        if pos > bt:
            skip = len(stream) - pos
            return Recovered([Repair(
                skip, None, len(stream), [Skip(skip, pos, ["end of file"])]
            )], pos, ["end of file"])
        return Error(pos, ["end of file"])


eof = Eof


def satisfy(test: Callable[[T], bool]) -> Parser[T, T]:
    def satisfy(stream: Sequence[T], pos: int, bt: int) -> Result[T]:
        if pos < len(stream):
            t = stream[pos]
            if test(t):
                return Ok(t, pos + 1)
        if pos > bt:
            cur = pos + 1
            while cur < len(stream):
                t = stream[cur]
                if test(t):
                    skip = cur - pos
                    return Recovered(
                        [Repair(skip, t, cur + 1, [Skip(skip, pos)])], pos
                    )
                cur += 1
        return Error(pos)

    return FnParser(satisfy)


def sym(s: T) -> Parser[T, T]:
    rs = repr(s)
    expected = [rs]

    def sym(stream: Sequence[T], pos: int, bt: int) -> Result[T]:
        if pos < len(stream):
            t = stream[pos]
            if t == s:
                return Ok(t, pos + 1)
        if pos > bt:
            ins = Repair(1, s, pos, [Insert(rs, pos, expected)])
            cur = pos + 1
            while cur < len(stream):
                t = stream[cur]
                if t == s:
                    skip = cur - pos
                    return Recovered(
                        [ins, Repair(skip, t, cur + 1, [Skip(skip, pos)])],
                        pos, expected
                    )
                cur += 1
            return Recovered([ins], pos, expected)
        return Error(pos, expected)

    return FnParser(sym)


def maybe(parser: Parser[T, V]) -> Parser[T, Optional[V]]:
    fn = parser.to_fn()

    def maybe(stream: Sequence[T], pos: int, bt: int) -> Result[Optional[V]]:
        r = fn(stream, pos, max(pos, bt))
        if r.pos != pos or isinstance(r, Ok):
            return r
        return Ok(None, pos, r.expected)

    return FnParser(maybe)


def many(parser: Parser[T, V]) -> Parser[T, List[V]]:
    fn = parser.to_fn()

    def many(stream: Sequence[T], pos: int, bt: int) -> Result[List[V]]:
        value: List[V] = []
        r = fn(stream, pos, max(pos, bt))
        while not isinstance(r, Error):
            if isinstance(r, Recovered):
                return many_recover(r, value, stream)
            value.append(r.value)
            pos = r.pos
            r = fn(stream, pos, max(pos, bt))
        if r.pos != pos:
            return r
        return Ok(value, pos, r.expected)

    def many_recover(
            r: Recovered[V], value: List[V],
            stream: Sequence[T]) -> Result[List[V]]:
        reps: Dict[int, Repair[List[V]]] = {}
        for p in r.repairs:
            rb = many(stream, p.pos, -1)
            if isinstance(rb, Ok):
                if rb.pos not in reps or p.cost < reps[rb.pos].cost:
                    pv = [*value, p.value, *rb.value]
                    reps[rb.pos] = Repair(p.cost, pv, rb.pos, p.ops)
            elif isinstance(rb, Recovered):
                p_ops = list(p.ops)
                for pb in rb.repairs:
                    cost = p.cost + pb.cost
                    if pb.pos not in reps or cost < reps[pb.pos].cost:
                        pv = [*value, p.value, *pb.value]
                        reps[pb.pos] = Repair(
                            cost, pv, pb.pos, chain(p_ops, pb.ops)
                        )
            elif rb.pos == p.pos:
                if p.pos not in reps or p.cost < reps[p.pos].cost:
                    pv = [*value, p.value]
                    reps[rb.pos] = Repair(p.cost, pv, p.pos, p.ops)
        if reps:
            return Recovered(list(reps.values()), r.pos, r.expected)
        return Error(r.pos, r.expected)

    return FnParser(many)


def label(parser: Parser[T, V], x: str) -> Parser[T, V]:
    fn = parser.to_fn()
    expected = [x]

    def label(stream: Sequence[T], pos: int, bt: int) -> Result[V]:
        r = fn(stream, pos, bt)
        if r.pos != pos:
            return r
        return r.expect(expected)

    return FnParser(label)


class InsertValue(Parser[T, V_co]):
    def __init__(self, value: V_co, l: str):
        self._value = value
        self._label = l

    def __call__(self, stream: Sequence[T], pos: int, bt: int) -> Result[V_co]:
        if pos > bt:
            return Recovered([Repair(
                1, self._value, pos, [Insert(self._label, pos, [self._label])]
            )], pos)
        return Error(pos)


insert = InsertValue


class Delay(Parser[T, V_co]):
    def __init__(self) -> None:
        def _fn(stream: Sequence[T], pos: int, bt: int) -> Result[V_co]:
            raise RuntimeError("Delayed parser was not defined")

        self._defined = False
        self._fn: ParseFn[T, V_co] = _fn

    def define(self, parser: Parser[T, V_co]) -> None:
        if self._defined:
            raise RuntimeError("Delayed parser was already defined")
        self._defined = True
        self._fn = parser.to_fn()

    def to_fn(self) -> ParseFn[T, V_co]:
        if self._defined:
            return self._fn
        return self

    def __call__(self, stream: Sequence[T], pos: int, bt: int) -> Result[V_co]:
        return self._fn(stream, pos, bt)


def sep_by(parser: Parser[T, V], sep: Parser[T, U]) -> Parser[T, List[V]]:
    return maybe(parser + many(sep.rseq(parser))).fmap(
        lambda v: [] if v is None else [v[0]] + v[1]
    )


def between(
        open: Parser[T, U], close: Parser[T, X],
        parser: Parser[T, V]) -> Parser[T, V]:
    return open.rseq(parser).lseq(close)


letter: Parser[str, str] = satisfy(str.isalpha).label("letter")
digit: Parser[str, str] = satisfy(str.isdigit).label("digit")
