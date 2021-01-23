from typing import Callable, Generic, Iterable, List, Optional, TypeVar

T = TypeVar('T')
M = TypeVar('M')


class Matchable(Generic[M]):
    def handle_match_op(self, op: M, ctx: 'Context[M]') -> bool:
        raise NotImplementedError()


class Context(Generic[M]):
    def __init__(self, term: Matchable[M]):
        self.stack: List[Matchable[M]] = [term]
        self.vars: List[Matchable[M]] = []

    def apply(self, op: M) -> bool:
        return self.stack.pop().handle_match_op(op, self)

    def push_term(self, term: Matchable[M]) -> None:
        self.stack.append(term)

    def push_terms(self, terms: Iterable[Matchable[M]]) -> None:
        self.stack.extend(terms)

    def push_var(self, term: Matchable[M]) -> None:
        self.vars.append(term)

    def get_var(self, idx: int) -> Matchable[M]:
        return self.vars[idx]


class MatchOpBuilder(Generic[M]):
    def build(self, bound: List[str]) -> M:
        raise NotImplementedError()


class ConstantOpBuilder(MatchOpBuilder[M]):
    def __init__(self, op: M):
        self.op = op

    def build(self, bound: List[str]) -> M:
        return self.op


class VarOpBuilder(MatchOpBuilder[M]):
    def __init__(
            self, name: str, make_bind: Callable[[], M],
            make_match: Callable[[int], M]):
        self.name = name
        self.make_bind = make_bind
        self.make_match = make_match

    def build(self, bound: List[str]) -> M:
        try:
            idx = bound.index(self.name)
        except ValueError:
            bound.append(self.name)
            return self.make_bind()
        else:
            return self.make_match(idx)


class Pattern(Generic[M]):
    def __init__(self, ops: List[M], bound: List[str]):
        self.ops = ops
        self.bound = bound

    def match(self, term: Matchable[M]) -> Optional[List[Matchable[M]]]:
        ctx = Context(term)
        for op in self.ops:
            if not ctx.apply(op):
                return None
        return ctx.vars


class PatternBuilder(Generic[M]):
    def __init__(self, ops: List[MatchOpBuilder[M]]):
        self.ops = ops

    @classmethod
    def from_op(cls, op: MatchOpBuilder[M]) -> 'PatternBuilder[M]':
        return PatternBuilder([op])

    def concat(self, other: 'PatternBuilder[M]') -> 'PatternBuilder[M]':
        return PatternBuilder(self.ops + other.ops)

    def build(self) -> Pattern[M]:
        bound: List[str] = []
        ops: List[M] = []
        for op in self.ops:
            ops.append(op.build(bound))
        return Pattern(ops, bound)
