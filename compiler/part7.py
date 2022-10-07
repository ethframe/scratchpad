from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from part3 import Actions, BinOpKind, interpret
from part4 import AssemblyActions
from part6 import StackItemsActions

A = TypeVar("A")


class Insn(ABC):
    @abstractmethod
    def visit(self, visitor: "InsnVisitor") -> None:
        ...


class InsnVisitor(ABC):
    @abstractmethod
    def visit_push_int(self, insn: "PushInt") -> None:
        ...

    @abstractmethod
    def visit_bin_op(self, insn: "BinOp") -> None:
        ...


class PushInt(Insn):
    def __init__(self, value: int):
        self.value = value

    def visit(self, visitor: InsnVisitor) -> None:
        visitor.visit_push_int(self)


class BinOp(Insn):
    def __init__(self, kind: BinOpKind):
        self.kind = kind

    def visit(self, visitor: InsnVisitor) -> None:
        visitor.visit_bin_op(self)


class InsnActions(Actions[list[Insn]]):
    def __init__(self) -> None:
        self.insns: list[Insn] = []

    def int_action(self, value: int) -> None:
        self.insns.append(PushInt(value))

    def bin_op_action(self, kind: BinOpKind) -> None:
        self.insns.append(BinOp(kind))

    def get_result(self) -> list[Insn]:
        return self.insns


def parse(source: str) -> list[Insn]:
    return interpret(source, InsnActions())


class ActionsAdapter(Generic[A], InsnVisitor):
    def __init__(self, actions: Actions[A]) -> None:
        self.actions = actions

    def visit_push_int(self, insn: PushInt) -> None:
        self.actions.int_action(insn.value)

    def visit_bin_op(self, insn: BinOp) -> None:
        self.actions.bin_op_action(insn.kind)


def interpret_insns(insns: list[Insn], actions: Actions[A]) -> A:
    visitor = ActionsAdapter(actions)
    for insn in insns:
        insn.visit(visitor)
    return actions.get_result()


def translate(source: str) -> str:
    insns = parse(source)
    interpret_insns(insns, StackItemsActions())
    return interpret_insns(insns, AssemblyActions())
