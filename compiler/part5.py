from io import StringIO

from part3 import Actions, interpret


class AssemblyActions(Actions[str]):
    def __init__(self) -> None:
        self.buffer = StringIO()
        self.buffer.write(".section .text\n")
        self.buffer.write(".global  _expr\n\n")
        self.buffer.write("_expr:\n")
        self.emit_prologue()

    def emit_prologue(self) -> None:
        self.buffer.write("\tpushq  %rbp\n")
        self.buffer.write("\tmovq   %rsp, %rbp\n")

    def emit_epilogue(self) -> None:
        self.buffer.write("\tmovq   %rbp, %rsp\n")
        self.buffer.write("\tpopq   %rbp\n")
        self.buffer.write("\tret\n\n")

    def emit_stack_check(self, argc: int) -> None:
        self.buffer.write("\tmovq   %rbp, %rax\n")
        self.buffer.write("\tsubq   %rsp, %rax\n")
        self.buffer.write(f"\tcmpq   ${argc * 8}, %rax\n")
        self.buffer.write("\tjl     _error\n")

    def emit_error_handler(self) -> None:
        self.buffer.write("_error:\n")
        self.buffer.write("\tcall   abort\n")

    def int_action(self, value: int) -> None:
        self.buffer.write(f"\tpushq  ${value}\n")

    def add_op_action(self) -> None:
        self.emit_stack_check(2)
        self.buffer.write("\tpopq   %rcx\n")
        self.buffer.write("\tpopq   %rax\n")
        self.buffer.write("\taddq   %rcx, %rax\n")
        self.buffer.write("\tpushq  %rax\n")

    def mul_op_action(self) -> None:
        self.emit_stack_check(2)
        self.buffer.write("\tpopq   %rcx\n")
        self.buffer.write("\tpopq   %rax\n")
        self.buffer.write("\timulq  %rcx\n")
        self.buffer.write("\tpushq  %rax\n")

    def get_result(self) -> str:
        self.emit_stack_check(1)
        self.buffer.write("\tpopq   %rax\n")
        self.emit_epilogue()
        self.emit_error_handler()
        return self.buffer.getvalue()


def translate(source: str) -> str:
    return interpret(source, AssemblyActions())


with open("p0.s", "w") as fp:
    fp.write(translate("1 2 + 3 *"))
