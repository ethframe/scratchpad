from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from part3 import Actions, interpret
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
    def visit_add(self, insn: "Add") -> None:
        ...

    @abstractmethod
    def visit_mul(self, insn: "Mul") -> None:
        ...


class PushInt(Insn):
    def __init__(self, value: int):
        self.value = value

    def visit(self, visitor: InsnVisitor) -> None:
        visitor.visit_push_int(self)


class Add(Insn):
    def visit(self, visitor: InsnVisitor) -> None:
        visitor.visit_add(self)


class Mul(Insn):
    def visit(self, visitor: InsnVisitor) -> None:
        visitor.visit_mul(self)


class InsnActions(Actions[list[Insn]]):
    def __init__(self) -> None:
        self.insns: list[Insn] = []

    def int_action(self, value: int) -> None:
        self.insns.append(PushInt(value))

    def add_op_action(self) -> None:
        self.insns.append(Add())

    def mul_op_action(self) -> None:
        self.insns.append(Mul())

    def get_result(self) -> list[Insn]:
        return self.insns


def parse(source: str) -> list[Insn]:
    return interpret(source, InsnActions())


class ActionsAdapter(Generic[A], InsnVisitor):
    def __init__(self, actions: Actions[A]) -> None:
        self.actions = actions

    def visit_push_int(self, insn: PushInt) -> None:
        self.actions.int_action(insn.value)

    def visit_add(self, insn: Add) -> None:
        self.actions.add_op_action()

    def visit_mul(self, insn: Mul) -> None:
        self.actions.mul_op_action()


def interpret_insns(insns: list[Insn], actions: Actions[A]) -> A:
    visitor = ActionsAdapter(actions)
    for insn in insns:
        insn.visit(visitor)
    return actions.get_result()


def translate(source: str) -> str:
    insns = parse(source)
    interpret_insns(insns, StackItemsActions())
    return interpret_insns(insns, AssemblyActions())
