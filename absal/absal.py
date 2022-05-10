from collections import defaultdict
from itertools import count
from typing import Callable, Dict, Optional, Set, Tuple, Union, final

Term = Union[
    "Val",
    "Op",
    "Var",
    "Lam",
    "App",
    "DupL",
    "DupR",
    "Sup",
]


class _Repr:
    def _repr_impl(self, seen: Set[object], names: Dict[object, str]) -> str:
        raise NotImplementedError()

    def _repr(self, seen: Set[object], names: Dict[object, str]) -> str:
        if self in seen:
            return "..."
        return self._repr_impl(seen.union((self,)), names)

    def __repr__(self) -> str:
        counter = count().__next__
        return self._repr(set(), defaultdict(lambda: f"v{counter()}"))


@final
class Val(_Repr):
    __slots__ = "val"

    def __init__(self, val: int):
        self.val = val

    def _repr_impl(self, seen: Set[object], names: Dict[object, str]) -> str:
        return repr(self.val)

    def reduce(self) -> Term:
        return self


@final
class Op(_Repr):
    __slots__ = "fn", "lhs", "rhs"

    def __init__(self, fn: Callable[[int, int], int], lhs: Term, rhs: Term):
        self.fn = fn
        self.lhs = lhs
        self.rhs = rhs

    def _repr_impl(self, seen: Set[object], names: Dict[object, str]) -> str:
        return f"({self.fn.__name__} " +\
            f"{self.lhs._repr(seen, names)} {self.rhs._repr(seen, names)})"

    def reduce(self) -> Term:
        lhs = self.lhs = self.lhs.reduce()
        rhs = self.rhs = self.rhs.reduce()
        if type(lhs) is Val and type(rhs) is Val:
            return Val(self.fn(lhs.val, rhs.val))
        if type(lhs) is Sup:
            a, b = _dup(rhs, lhs.tok)
            return Sup(
                lhs.tok,
                Op(self.fn, lhs.lhs, a),
                Op(self.fn, lhs.rhs, b)
            )
        if type(rhs) is Sup:
            a, b = _dup(lhs, rhs.tok)
            return Sup(
                rhs.tok,
                Op(self.fn, a, rhs.lhs),
                Op(self.fn, b, rhs.rhs)
            )
        return self


@final
class Var(_Repr):
    __slots__ = "term"

    def __init__(self, term: Optional[Term] = None):
        self.term = term

    def _repr_impl(self, seen: Set[object], names: Dict[object, str]) -> str:
        return names[self]

    def reduce(self) -> Term:
        if self.term is not None:
            return self.term.reduce()
        return self


@final
class Lam(_Repr):
    __slots__ = "arg", "body"

    def __init__(self, arg: Var, body: Term):
        self.arg = arg
        self.body = body

    def _repr_impl(self, seen: Set[object], names: Dict[object, str]) -> str:
        return f"(lambda ({self.arg._repr(seen, names)}) " +\
            f"{self.body._repr(seen, names)})"

    def reduce(self) -> Term:
        return self


@final
class App(_Repr):
    __slots__ = "lam", "arg"

    def __init__(self, lam: Term, arg: Term):
        self.lam = lam
        self.arg = arg

    def _repr_impl(self, seen: Set[object], names: Dict[object, str]) -> str:
        return f"({self.lam._repr(seen, names)} {self.arg._repr(seen, names)})"

    def reduce(self) -> Term:
        lam = self.lam = self.lam.reduce()
        if type(lam) is Lam:
            lam.arg.term = self.arg
            return lam.body.reduce()
        if type(lam) is Sup:
            a, b = _dup(self.arg, lam.tok)
            return Sup(lam.tok, App(lam.lhs, a), App(lam.rhs, b))
        return self


class Tok:
    __slots__ = ()


@final
class Dup:
    __slots__ = "tok", "term", "lhs", "rhs"

    def __init__(self, tok: Tok, term: Term):
        self.tok = tok
        self.term = term
        self.lhs: Optional[DupL] = None
        self.rhs: Optional[DupR] = None

    def duplicate(self) -> None:
        term = self.term = self.term.reduce()
        if type(term) is Val:
            if self.lhs is not None:
                assert self.lhs.term is None
                self.lhs.term = term
            if self.rhs is not None:
                assert self.rhs.term is None
                self.rhs.term = term
            return
        if type(term) is Lam:
            x0 = Var()
            x1 = Var()
            term.arg.term = Sup(self.tok, x0, x1)
            b0, b1 = _dup(term.body, self.tok)
            if self.lhs is not None:
                assert self.lhs.term is None
                self.lhs.term = Lam(x0, b0)
            if self.rhs is not None:
                assert self.rhs.term is None
                self.rhs.term = Lam(x1, b1)
            return
        if type(term) is Sup:
            if term.tok is self.tok:
                if self.lhs is not None:
                    assert self.lhs.term is None
                    self.lhs.term = term.lhs
                if self.rhs is not None:
                    assert self.rhs.term is None
                    self.rhs.term = term.rhs
            else:
                xa, ya = _dup(term.lhs, self.tok)
                xb, yb = _dup(term.rhs, self.tok)

                if self.lhs is not None:
                    assert self.lhs.term is None
                    self.lhs.term = Sup(term.tok, xa, xb)
                if self.rhs is not None:
                    assert self.rhs.term is None
                    self.rhs.term = Sup(term.tok, ya, yb)
            return


@final
class DupL(_Repr):
    __slots__ = "dup", "term"

    def __init__(self, dup: Dup):
        self.dup = dup
        self.term: Optional[Term] = None

    def _repr_impl(self, seen: Set[object], names: Dict[object, str]) -> str:
        return f"<({self.dup.term._repr(seen, names)})"

    def reduce(self) -> Term:
        if self.term is None:
            self.dup.duplicate()
        if self.term is not None:
            return self.term.reduce()
        return self


@final
class DupR(_Repr):
    __slots__ = "dup", "term"

    def __init__(self, dup: Dup):
        self.dup = dup
        self.term: Optional[Term] = None

    def _repr_impl(self, seen: Set[object], names: Dict[object, str]) -> str:
        return f"({self.dup.term._repr(seen, names)})>"

    def reduce(self) -> Term:
        if self.term is None:
            self.dup.duplicate()
        if self.term is not None:
            return self.term.reduce()
        return self


def _dup(term: Term, tok: Tok) -> Tuple[DupL, DupR]:
    dup = Dup(tok, term)
    lhs = dup.lhs = DupL(dup)
    rhs = dup.rhs = DupR(dup)
    return lhs, rhs


@final
class Sup(_Repr):
    __slots__ = "tok", "lhs", "rhs"

    def __init__(self, tok: Tok, lhs: Term, rhs: Term):
        self.tok = tok
        self.lhs = lhs
        self.rhs = rhs

    def _repr_impl(self, seen: Set[object], names: Dict[object, str]) -> str:
        return f"{{{self.lhs._repr(seen, names)} " +\
            f"{self.rhs._repr(seen, names)}}}"

    def reduce(self) -> Term:
        return self


def dup(term: Term) -> Tuple[DupL, DupR]:
    return _dup(term, Tok())


def run(term: Term, steps: int = 1) -> Term:
    print(term)
    for _ in range(steps):
        term = term.reduce()
        print("~>", term)
    return term
