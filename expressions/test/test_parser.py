import pytest
from expressions.parser import Binary, Node, Term, Unary, parse

DATA_POSITIVE = [
    (
        "a + b + c",
        Binary(
            op="+",
            lhs=Binary(
                op="+",
                lhs=Term("ident", "a"),
                rhs=Term("ident", "b")
            ),
            rhs=Term("ident", "c")
        )
    ),
    (
        "a + (b + c)",
        Binary(
            op="+",
            lhs=Term("ident", "a"),
            rhs=Binary(
                op="+",
                lhs=Term("ident", "b"),
                rhs=Term("ident", "c")
            )
        )
    ),
    (
        "a * b + c",
        Binary(
            op="+",
            lhs=Binary(
                op="*",
                lhs=Term("ident", "a"),
                rhs=Term("ident", "b")
            ),
            rhs=Term("ident", "c")
        )
    ),
    (
        "a + b * c",
        Binary(
            op="+",
            lhs=Term("ident", "a"),
            rhs=Binary(
                op="*",
                lhs=Term("ident", "b"),
                rhs=Term("ident", "c")
            )
        )
    ),
    (
        "-a + b",
        Binary(
            op="+",
            lhs=Unary(op="-", arg=Term("ident", "a")),
            rhs=Term("ident", "b")
        )
    ),
    (
        "-a ^ b",
        Binary(
            op="^",
            lhs=Unary(op="-", arg=Term("ident", "a")),
            rhs=Term("ident", "b")
        )
    ),
    (
        "a ^ b ^ c",
        Binary(
            op="^",
            lhs=Term("ident", "a"),
            rhs=Binary(
                op="^",
                lhs=Term("ident", "b"),
                rhs=Term("ident", "c")
            )
        )
    ),
    (
        "-a!",
        Unary(op="-", arg=Unary(op="!", arg=Term("ident", "a")))
    ),
    (
        "(-a)!",
        Unary(op="!", arg=Unary(op="-", arg=Term("ident", "a")))
    ),
    (
        "--+a",
        Unary(
            op="-",
            arg=Unary(
                op="-",
                arg=Unary(op="+", arg=Term("ident", "a"))
            )
        )
    ),
]


@pytest.mark.parametrize("src, ast", DATA_POSITIVE)
def test_positive(src: str, ast: Node) -> None:
    assert parse(src) == ast


DATA_NEGATIVE = [
    "a b",
    "a + * b",
    "((a)",
    "(a))",
    "a +",
    "(a +) b",
]


@pytest.mark.parametrize("src", DATA_NEGATIVE)
def test_negative(src: str) -> None:
    with pytest.raises(ValueError):
        parse(src)
