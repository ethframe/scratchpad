from io import StringIO

from part3 import Actions, interpret


class AssemblyActions(Actions[str]):
    def __init__(self) -> None:
        self.buffer = StringIO()
        self.buffer.write(".global _expr\n\n")
        self.buffer.write(".section .text\n")
        self.buffer.write("_expr:\n")

    def int_action(self, value: int) -> None:
        self.buffer.write(f"\tpushq ${value}\n")

    def add_op_action(self) -> None:
        self.buffer.write("\tpopq  %rcx\n")
        self.buffer.write("\tpopq  %rax\n")
        self.buffer.write("\taddq  %rcx, %rax\n")
        self.buffer.write("\tpushq %rax\n")

    def mul_op_action(self) -> None:
        self.buffer.write("\tpopq  %rcx\n")
        self.buffer.write("\tpopq  %rax\n")
        self.buffer.write("\timulq %rcx\n")
        self.buffer.write("\tpushq %rax\n")

    def get_result(self) -> str:
        self.buffer.write("\tpopq  %rax\n")
        self.buffer.write("\tret\n")
        return self.buffer.getvalue()


def translate(source: str) -> str:
    return interpret(source, AssemblyActions())


with open("p0.s", "w") as fp:
    fp.write(translate("1 2 + 3 *"))
