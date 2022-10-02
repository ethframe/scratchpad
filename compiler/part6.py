from part3 import Actions, interpret
from part4 import AssemblyActions


class StackItemsError(Exception):
    pass


class StackItemsActions(Actions[None]):
    def __init__(self) -> None:
        self.count = 0

    def int_action(self, value: int) -> None:
        self.count += 1

    def add_op_action(self) -> None:
        if self.count < 2:
            raise StackItemsError()
        self.count -= 1

    def mul_op_action(self) -> None:
        if self.count < 2:
            raise StackItemsError()
        self.count -= 1

    def get_result(self) -> None:
        if self.count != 1:
            raise StackItemsError()


def translate(source: str) -> str:
    interpret(source, StackItemsActions())
    return interpret(source, AssemblyActions())
