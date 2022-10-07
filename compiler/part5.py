from io import StringIO

from part3 import Actions, BinOpKind, interpret


class AssemblyActions(Actions[str]):
    def __init__(self) -> None:
        self.buffer = StringIO()
        self._emit_header()
        self._emit_prologue()

    def _emit(self, insn: str, *args: str) -> None:
        if len(args) == 0:
            line = insn
        else:
            line = insn.ljust(8) + ", ".join(args)
        self.buffer.write("\t" + line + "\n")

    def _emit_header(self) -> None:
        self.buffer.write(".global _expr\n\n")
        self.buffer.write(".section .text\n")
        self.buffer.write("_expr:\n")

    def _emit_prologue(self) -> None:
        self._emit("pushq", "%rbp")
        self._emit("movq",  "%rsp", "%rbp")

    def _emit_epilogue(self) -> None:
        self._emit("movq", "%rbp", "%rsp")
        self._emit("popq", "%rbp")
        self._emit("ret")

    def _emit_stack_check(self, argc: int) -> None:
        self._emit("movq", "%rbp", "%rax")
        self._emit("subq", "%rsp", "%rax")
        self._emit("cmpq", f"${argc * 8}", "%rax")
        self._emit("jl",   "_error")

    def _emit_error_handler(self) -> None:
        self.buffer.write("_error:\n")
        self._emit("call", "abort")

    def int_action(self, value: int) -> None:
        self._emit("pushq", f"${value}")

    def bin_op_action(self, kind: BinOpKind) -> None:
        self._emit_stack_check(2)
        self._emit("popq",  "%rcx")
        self._emit("popq",  "%rax")
        match kind:
            case BinOpKind.AddOp:
                self._emit("addq",  "%rcx", "%rax")
            case BinOpKind.MulOp:
                self._emit("imulq", "%rcx")
        self._emit("pushq", "%rax")

    def get_result(self) -> str:
        self._emit_stack_check(1)
        self._emit("popq", "%rax")
        self._emit_epilogue()
        self._emit_error_handler()
        return self.buffer.getvalue()


def translate(source: str) -> str:
    return interpret(source, AssemblyActions())
