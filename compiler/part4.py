from io import StringIO

from part3 import Actions, BinOpKind, interpret


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
                self.stack.append((a + b) & (2 ** 64 - 1))
            case BinOpKind.MulOp:
                self.stack.append((a * b) & (2 ** 64 - 1))

    def get_result(self) -> int:
        return self.stack.pop()


def evaluate(source: str) -> int:
    return interpret(source, StackAction())


class AssemblyActions(Actions[str]):
    def __init__(self) -> None:
        self.buffer = StringIO()
        self.buffer.write(".global _expr\n\n")
        self.buffer.write(".section .text\n")
        self.buffer.write("_expr:\n")

    def int_action(self, value: int) -> None:
        self.buffer.write(f"\tpushq   ${value}\n")

    def bin_op_action(self, kind: BinOpKind) -> None:
        self.buffer.write("\tpopq    %rcx\n")
        self.buffer.write("\tpopq    %rax\n")
        match kind:
            case BinOpKind.AddOp:
                self.buffer.write("\taddq    %rcx, %rax\n")
            case BinOpKind.MulOp:
                self.buffer.write("\timulq   %rcx\n")
        self.buffer.write("\tpushq   %rax\n")

    def get_result(self) -> str:
        self.buffer.write("\tpopq    %rax\n")
        self.buffer.write("\tret\n")
        return self.buffer.getvalue()


def translate(source: str) -> str:
    return interpret(source, AssemblyActions())
