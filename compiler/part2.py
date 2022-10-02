from enum import Enum


class TokenKind(Enum):
    Space = 0
    Integer = 1
    AddOp = 2
    MulOp = 3


class ScanError(Exception):
    pass


def scan(source: str, pos: int) -> tuple[TokenKind | None, int]:
    if pos == len(source):
        return None, pos
    c = source[pos]
    pos += 1
    if c == " ":
        return TokenKind.Space, pos
    if c == "0":
        if pos < len(source) and source[pos] != " ":
            raise ScanError()
        return TokenKind.Integer, pos
    if "1" <= c and c <= "9":
        while pos < len(source):
            c = source[pos]
            if c == " ":
                break
            if c < "0" or c > "9":
                raise ScanError()
            pos += 1
        return TokenKind.Integer, pos
    if c == "+":
        if pos < len(source) and source[pos] != " ":
            raise ScanError()
        return TokenKind.AddOp, pos
    if c == "*":
        if pos < len(source) and source[pos] != " ":
            raise ScanError()
        return TokenKind.MulOp, pos
    raise ScanError()


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
