from dataclasses import dataclass
from typing import List

from .matching import (
    ConstantOpBuilder, Context, Matchable, MatchOpBuilder, VarOpBuilder
)

Stack = List[Matchable['TermOp']]
Env = List[Matchable['TermOp']]


class Term(Matchable['TermOp']):
    pass


@dataclass
class Val(Term):
    value: str

    def handle_match_op(self, op: 'TermOp', ctx: Context['TermOp']) -> bool:
        return op.handle_val(self, ctx)


@dataclass
class Func(Term):
    name: str
    args: List[Term]

    def handle_match_op(self, op: 'TermOp', ctx: Context['TermOp']) -> bool:
        return op.handle_func(self, ctx)


class TermOp:
    def handle_term(self, term: Term, ctx: Context['TermOp']) -> bool:
        return False

    def handle_func(self, term: Func, ctx: Context['TermOp']) -> bool:
        return self.handle_term(term, ctx)

    def handle_val(self, term: Val, ctx: Context['TermOp']) -> bool:
        return self.handle_term(term, ctx)


class MatchFunc(TermOp):
    def __init__(self, name: str, arity: int):
        self.name = name
        self.arity = arity

    def handle_func(self, term: Func, ctx: Context[TermOp]) -> bool:
        if self.name != term.name or self.arity != len(term.args):
            return False
        ctx.push_terms(reversed(term.args))
        return True


class MatchVal(TermOp):
    def __init__(self, value: str):
        self.value = value

    def handle_val(self, term: Val, ctx: Context[TermOp]) -> bool:
        return self.value == term.value


class BindVar(TermOp):
    def handle_term(self, term: Term, ctx: Context[TermOp]) -> bool:
        ctx.push_var(term)
        return True


class MatchVar(TermOp):
    def __init__(self, idx: int):
        self.idx = idx

    def handle_term(self, term: Term, ctx: Context[TermOp]) -> bool:
        return ctx.get_var(self.idx) == term


class MatchAny(TermOp):
    def handle_term(self, term: Term, ctx: Context[TermOp]) -> bool:
        return True


TermOpBuilder = MatchOpBuilder[TermOp]


def func(name: str, *args: List[TermOpBuilder]) -> List[TermOpBuilder]:
    result: List[TermOpBuilder] = [
        ConstantOpBuilder(MatchFunc(name, len(args)))
    ]
    for arg in args:
        result.extend(arg)
    return result


def val(value: str) -> List[TermOpBuilder]:
    return [ConstantOpBuilder(MatchVal(value))]


def v(name: str) -> List[TermOpBuilder]:
    return [VarOpBuilder(name, BindVar, MatchVar)]


_ = [ConstantOpBuilder(MatchAny())]
