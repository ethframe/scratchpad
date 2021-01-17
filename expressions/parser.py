import re
from dataclasses import dataclass

from .lexer import Lexer, Token, split_tokens


class Node:
    pass


@dataclass
class Binary(Node):
    op: str
    lhs: Node
    rhs: Node


@dataclass
class Unary(Node):
    op: str
    arg: Node


@dataclass
class Term(Node):
    kind: str
    value: str


TOKENS = re.compile(r"""
 (?P<ident>[a-zA-Z_][a-zA-Z_0-9]*)
|(?P<num>[0-9]+)
|(?P<op>[+\-*/()!^])
|[ \n\r\t]+
""", re.VERBOSE)

EOF = Token("eof", "")

CLOSED = {
    "(": (0, ")"),
}

PREFIX = {
    "+": 5,
    "-": 5,
}

INFIX = {
    "+": (0, 1),
    "-": (0, 1),
    "*": (2, 3),
    "/": (2, 3),
    "^": (4, 4),
}

POSTFIX = {
    "!": 6
}


def parse_prim(lexer: Lexer, tok: Token) -> Node:
    if tok.kind in {"ident", "num"}:
        lexer.advance()
        return Term(tok.kind, tok.value)
    raise ValueError("Unexpected token")


def parse_bp(lexer: Lexer, bp: int) -> Node:
    tok = lexer.peek()
    if tok.kind == "op":
        if tok.value in CLOSED:
            rbp, end = CLOSED[tok.value]
            lexer.advance()
            expr = parse_bp(lexer, rbp)
            if lexer.peek() != Token("op", end):
                raise ValueError("Unexpected token")
            lexer.advance()
        elif tok.value in PREFIX:
            rbp = PREFIX[tok.value]
            lexer.advance()
            expr = Unary(tok.value, parse_bp(lexer, rbp))
        else:
            raise ValueError("Unknown prefix operator")
    elif tok == EOF:
        raise ValueError("Unexpected end of file")
    else:
        expr = parse_prim(lexer, tok)
    while True:
        tok = lexer.peek()
        if tok.kind == "op":
            if tok.value in INFIX:
                lbp, rbp = INFIX[tok.value]
                if lbp < bp:
                    break
                lexer.advance()
                expr = Binary(tok.value, expr, parse_bp(lexer, rbp))
            elif tok.value in POSTFIX:
                lbp = POSTFIX[tok.value]
                if lbp < bp:
                    break
                lexer.advance()
                expr = Unary(tok.value, expr)
            else:
                break
        elif tok == EOF:
            break
        else:
            raise ValueError("Unexpected token")
    return expr


def parse(src: str) -> Node:
    lexer = Lexer(split_tokens(src, TOKENS, EOF))
    expr = parse_bp(lexer, 0)
    if lexer.peek() != EOF:
        raise ValueError("Unexpected token")
    return expr
