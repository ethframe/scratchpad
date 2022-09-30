from enum import Enum
from unittest import TestCase


class TokenKind(Enum):
    Space = 0
    Integer = 1
    AddOp = 2
    MulOp = 3


def scan(source: str, pos: int) -> tuple[TokenKind | None, int]:
    if pos == len(source):
        return None, pos
    c = source[pos]
    pos += 1
    if c == " ":
        return TokenKind.Space, pos
    if "0" <= c and c <= "9":
        while pos < len(source):
            c = source[pos]
            if c == " ":
                break
            if c < "0" or c > "9":
                raise RuntimeError()
            pos += 1
        return TokenKind.Integer, pos
    if c == "+":
        return TokenKind.AddOp, pos
    if c == "*":
        return TokenKind.MulOp, pos
    raise RuntimeError()


def evaluate(source: str) -> int:
    stack: list[int] = []
    pos = 0
    while True:
        token, end = scan(source, pos)
        if token is None:
            break
        elif token is TokenKind.Integer:
            value = int(source[pos:end])
            stack.append(value)
        elif token is TokenKind.AddOp:
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b)
        elif token is TokenKind.MulOp:
            b = stack.pop()
            a = stack.pop()
            stack.append(a * b)
        pos = end
    return stack.pop()


class TestEvaluate1(TestCase):
    def test_evaluate_1(self) -> None:
        for source, get_result in [
            ("1 2 + 3 +", 6),
            ("1 2 3 * +", 7),
            ("1 2 + 3 *", 9),
        ]:
            with self.subTest():
                self.assertEqual(evaluate(source), get_result)
