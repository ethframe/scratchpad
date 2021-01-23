from dataclasses import dataclass
from typing import List

from .matching import (
    ConstantOpBuilder, Context, Matchable, PatternBuilder, VarOpBuilder
)


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


def func(name: str, *args: PatternBuilder[TermOp]) -> PatternBuilder[TermOp]:
    builder = PatternBuilder[TermOp].from_op(
        ConstantOpBuilder(MatchFunc(name, len(args)))
    )
    for arg in args:
        builder = builder.concat(arg)
    return builder


def val(value: str) -> PatternBuilder[TermOp]:
    return PatternBuilder.from_op(ConstantOpBuilder(MatchVal(value)))


def v(name: str) -> PatternBuilder[TermOp]:
    return PatternBuilder.from_op(VarOpBuilder(name, BindVar, MatchVar))


_ = PatternBuilder.from_op(ConstantOpBuilder(MatchAny()))
