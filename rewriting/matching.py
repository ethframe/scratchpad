from typing import Callable, Generic, List, Optional, TypeVar


T = TypeVar('T')
M = TypeVar('M')


class Matchable(Generic[M]):
    def handle_match_op(
            self, op: M, stack: List['Matchable[M]'],
            env: List['Matchable[M]']) -> bool:
        raise NotImplementedError()


class MatchOpBuilder(Generic[M]):
    def build(self, bound: List[str]) -> M:
        raise NotImplementedError()


class ConstantBuilder(MatchOpBuilder[M]):
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
        stack: List[Matchable[M]] = [term]
        env: List[Matchable[M]] = []
        for op in self.ops:
            term = stack.pop()
            if not term.handle_match_op(op, stack, env):
                return None
        return env


def build_pattern(builders: List[MatchOpBuilder[M]]) -> Pattern[M]:
    bound: List[str] = []
    result: List[M] = []
    for builder in builders:
        result.append(builder.build(bound))
    return Pattern(result, bound)
