import re
from dataclasses import dataclass
from typing import Callable, Dict, Tuple

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


NudParser = Callable[[Lexer], Node]
LedParser = Callable[[Lexer, Node], Node]


def prefix(op: str, bp: int) -> NudParser:
    def parser(lexer: Lexer) -> Node:
        return Unary(op, parse_expr(lexer, bp))
    return parser


def closed_drop(bp: int, end: str) -> NudParser:
    def parser(lexer: Lexer) -> Node:
        expr = parse_until(lexer, bp, Token("op", end))
        lexer.advance()
        return expr
    return parser


def infix(lbp: int, op: str, rbp: int) -> Tuple[int, LedParser]:
    def parser(lexer: Lexer, expr: Node) -> Node:
        return Binary(op, expr, parse_expr(lexer, rbp))
    return (lbp, parser)


def infix_left(op: str, bp: int) -> Tuple[int, LedParser]:
    return infix(bp, op, bp + 1)


def infix_right(op: str, bp: int) -> Tuple[int, LedParser]:
    return infix(bp, op, bp)


def postfix(lbp: int, op: str) -> Tuple[int, LedParser]:
    def parser(lexer: Lexer, expr: Node) -> Node:
        return Unary(op, expr)
    return (lbp, parser)


NUD: Dict[str, NudParser] = {
    "+": prefix("pos", 5),
    "-": prefix("neg", 5),
    "(": closed_drop(0, ")"),
}

LED: Dict[str, Tuple[int, LedParser]] = {
    "+": infix_left("add", 0),
    "-": infix_left("sub", 0),
    "*": infix_left("mul", 2),
    "/": infix_left("div", 2),
    "^": infix_right("pow", 4),
    "!": postfix(6, "fact"),
}


def parse_prim(lexer: Lexer, tok: Token) -> Node:
    if tok.kind in {"ident", "num"}:
        lexer.advance()
        return Term(tok.kind, tok.value)
    raise ValueError("Unexpected token")


def parse_expr(lexer: Lexer, bp: int) -> Node:
    tok = lexer.peek()
    if tok.kind == "op" and tok.value in NUD:
        parse_nud = NUD[tok.value]
        lexer.advance()
        expr = parse_nud(lexer)
    else:
        expr = parse_prim(lexer, tok)
    tok = lexer.peek()
    while tok.kind == "op" and tok.value in LED:
        lbp, parse_led = LED[tok.value]
        if lbp < bp:
            break
        lexer.advance()
        expr = parse_led(lexer, expr)
        tok = lexer.peek()
    return expr


def parse_until(lexer: Lexer, bp: int, tok: Token) -> Node:
    expr = parse_expr(lexer, bp)
    if lexer.peek() != tok:
        raise ValueError("Unexpected token")
    return expr


def parse(src: str) -> Node:
    lexer = Lexer(split_tokens(src, TOKENS, EOF))
    return parse_until(lexer, 0, EOF)
