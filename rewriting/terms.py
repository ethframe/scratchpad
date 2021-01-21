from dataclasses import dataclass
from typing import List

from .matching import ConstantBuilder, Matchable, MatchOpBuilder, VarOpBuilder

Stack = List[Matchable['TermOp']]
Env = List[Matchable['TermOp']]


class Term(Matchable['TermOp']):
    pass


@dataclass
class Val(Term):
    value: str

    def handle_match_op(self, op: 'TermOp', stack: Stack, env: Env) -> bool:
        return op.handle_val(self, stack, env)


@dataclass
class Func(Term):
    name: str
    args: List[Term]

    def handle_match_op(self, op: 'TermOp', stack: Stack, env: Env) -> bool:
        return op.handle_func(self, stack, env)


class TermOp:
    def handle_term(self, term: Term, stack: Stack, env: Env) -> bool:
        return False

    def handle_func(self, term: Func, stack: Stack, env: Env) -> bool:
        return self.handle_term(term, stack, env)

    def handle_val(self, term: Val, stack: Stack, env: Env) -> bool:
        return self.handle_term(term, stack, env)


class Unwrap(TermOp):
    def __init__(self, name: str, arity: int):
        self.name = name
        self.arity = arity

    def handle_func(self, term: Func, stack: Stack, env: Env) -> bool:
        if self.name != term.name or self.arity != len(term.args):
            return False
        stack.extend(reversed(term.args))
        return True


class MatchVal(TermOp):
    def __init__(self, value: str):
        self.value = value

    def handle_val(self, term: Val, stack: Stack, env: Env) -> bool:
        return self.value == term.value


class BindVar(TermOp):
    def handle_term(self, term: Term, stack: Stack, env: Env) -> bool:
        env.append(term)
        return True


class MatchVar(TermOp):
    def __init__(self, idx: int):
        self.idx = idx

    def handle_term(self, term: Term, stack: Stack, env: Env) -> bool:
        return env[self.idx] == term


TermOpBuilder = MatchOpBuilder[TermOp]


def func(name: str, *args: List[TermOpBuilder]) -> List[TermOpBuilder]:
    result: List[TermOpBuilder] = [ConstantBuilder(Unwrap(name, len(args)))]
    for arg in args:
        result.extend(arg)
    return result


def val(value: str) -> List[TermOpBuilder]:
    return [ConstantBuilder(MatchVal(value))]


def v(name: str) -> List[TermOpBuilder]:
    return [VarOpBuilder(name, BindVar, MatchVar)]
