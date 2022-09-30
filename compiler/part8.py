from enum import Enum


class TokenKind(Enum):
    Space = 0
    Integer = 1
    AddOp = 2
    MulOp = 3
    LParen = 4
    RParen = 5
    MinusMinus = 6
    Ident = 7


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
    if c == "(":
        return TokenKind.LParen, pos
    if c == ")":
        return TokenKind.RParen, pos
    if c == "-":
        if pos < len(source):
            raise RuntimeError()
        c = source[pos]
        pos += 1
        if c != "-":
            raise RuntimeError()
        return TokenKind.MinusMinus, pos
    raise RuntimeError()
