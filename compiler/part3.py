from abc import abstractmethod
from typing import Generic, TypeVar

from part2 import TokenKind, scan

A = TypeVar("A")


class Actions(Generic[A]):
    @abstractmethod
    def int_action(self, value: int) -> None:
        ...

    @abstractmethod
    def add_op_action(self) -> None:
        ...

    @abstractmethod
    def mul_op_action(self) -> None:
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
            act.add_op_action()
        elif token is TokenKind.MulOp:
            act.mul_op_action()
        pos = end
    return act.get_result()


class StackActions(Actions[int]):
    def __init__(self) -> None:
        self.stack: list[int] = []

    def int_action(self, value: int) -> None:
        self.stack.append(value)

    def add_op_action(self) -> None:
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a + b)

    def mul_op_action(self) -> None:
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a * b)

    def get_result(self) -> int:
        return self.stack.pop()


def evaluate(source: str) -> int:
    return interpret(source, StackActions())
