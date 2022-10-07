from abc import abstractmethod
from enum import Enum
from typing import Generic, TypeVar

from part2 import TokenKind, scan

A = TypeVar("A")


class BinOpKind(Enum):
    AddOp = 0
    MulOp = 1


class Actions(Generic[A]):
    @abstractmethod
    def int_action(self, value: int) -> None:
        ...

    @abstractmethod
    def bin_op_action(self, kind: BinOpKind) -> None:
        ...

    @abstractmethod
    def get_result(self) -> A:
        ...


def interpret(source: str, act: Actions[A]) -> A:
    pos = 0
    while True:
        token, end = scan(source, pos)
        if token is None:
            break
        elif token is TokenKind.Integer:
            value = int(source[pos:end])
            act.int_action(value)
        elif token is TokenKind.AddOp:
            act.bin_op_action(BinOpKind.AddOp)
        elif token is TokenKind.MulOp:
            act.bin_op_action(BinOpKind.MulOp)
        pos = end
    return act.get_result()


class StackAction(Actions[int]):
    def __init__(self) -> None:
        self.stack: list[int] = []

    def int_action(self, value: int) -> None:
        self.stack.append(value)

    def bin_op_action(self, kind: BinOpKind) -> None:
        b = self.stack.pop()
        a = self.stack.pop()
        match kind:
            case BinOpKind.AddOp:
                self.stack.append(a + b)
            case BinOpKind.MulOp:
                self.stack.append(a * b)

    def get_result(self) -> int:
        return self.stack.pop()


def evaluate(source: str) -> int:
    return interpret(source, StackAction())
