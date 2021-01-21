from dataclasses import dataclass
from typing import List, Optional

Stack = List['Term']
Env = List['Term']


class Term:
    def handle_match_op(self, op: 'MatchOp', stack: Stack, env: Env) -> bool:
        raise NotImplementedError()


@dataclass
class Val(Term):
    value: str

    def handle_match_op(self, op: 'MatchOp', stack: Stack, env: Env) -> bool:
        return op.handle_val(self, stack, env)


@dataclass
class Func(Term):
    name: str
    args: List[Term]

    def handle_match_op(self, op: 'MatchOp', stack: Stack, env: Env) -> bool:
        return op.handle_func(self, stack, env)


class MatchOp:
    def handle_term(self, term: Term, stack: Stack, env: Env) -> bool:
        return False

    def handle_func(self, term: Func, stack: Stack, env: Env) -> bool:
        return self.handle_term(term, stack, env)

    def handle_val(self, term: Val, stack: Stack, env: Env) -> bool:
        return self.handle_term(term, stack, env)


class MatchOpBuilder:
    def build(self, bound: List[str]) -> MatchOp:
        raise NotImplementedError()


class ConstantBuilder(MatchOpBuilder):
    def __init__(self, op: MatchOp):
        self.op = op

    def build(self, bound: List[str]) -> MatchOp:
        return self.op


class Unwrap(MatchOp):
    def __init__(self, name: str, arity: int):
        self.name = name
        self.arity = arity

    def handle_func(self, term: Func, stack: Stack, env: Env) -> bool:
        if self.name != term.name or self.arity != len(term.args):
            return False
        stack.extend(reversed(term.args))
        return True


class MatchVal(MatchOp):
    def __init__(self, value: str):
        self.value = value

    def handle_val(self, term: Val, stack: Stack, env: Env) -> bool:
        return self.value == term.value


class VarOpBuilder(MatchOpBuilder):
    def __init__(self, name: str):
        self.name = name

    def build(self, bound: List[str]) -> MatchOp:
        try:
            idx = bound.index(self.name)
        except ValueError:
            bound.append(self.name)
            return BindVar()
        else:
            return MatchVar(idx)


class BindVar(MatchOp):
    def handle_term(self, term: Term, stack: Stack, env: Env) -> bool:
        env.append(term)
        return True


class MatchVar(MatchOp):
    def __init__(self, idx: int):
        self.idx = idx

    def handle_term(self, term: Term, stack: Stack, env: Env) -> bool:
        return env[self.idx] == term


class Pattern:
    def __init__(self, ops: List[MatchOp], bound: List[str]):
        self.ops = ops
        self.bound = bound

    def match(self, term: Term) -> Optional[List[Term]]:
        stack: List[Term] = [term]
        env: List[Term] = []
        for op in self.ops:
            term = stack.pop()
            if not term.handle_match_op(op, stack, env):
                return None
        return env


def build_pattern(builders: List[MatchOpBuilder]) -> Pattern:
    bound: List[str] = []
    result: List[MatchOp] = []
    for builder in builders:
        result.append(builder.build(bound))
    return Pattern(result, bound)


def func(name: str, *args: List[MatchOpBuilder]) -> List[MatchOpBuilder]:
    result: List[MatchOpBuilder] = [ConstantBuilder(Unwrap(name, len(args)))]
    for arg in args:
        result.extend(arg)
    return result


def val(value: str) -> List[MatchOpBuilder]:
    return [ConstantBuilder(MatchVal(value))]


def v(name: str) -> List[MatchOpBuilder]:
    return [VarOpBuilder(name)]
