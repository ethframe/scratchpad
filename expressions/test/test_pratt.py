import pytest

from expressions.pratt import Binary, Node, Term, Unary, parse

DATA_POSITIVE = [
    (
        "a + b + c",
        Binary(
            op="add",
            lhs=Binary(
                op="add",
                lhs=Term("ident", "a"),
                rhs=Term("ident", "b")
            ),
            rhs=Term("ident", "c")
        )
    ),
    (
        "a + (b + c)",
        Binary(
            op="add",
            lhs=Term("ident", "a"),
            rhs=Binary(
                op="add",
                lhs=Term("ident", "b"),
                rhs=Term("ident", "c")
            )
        )
    ),
    (
        "a * b + c",
        Binary(
            op="add",
            lhs=Binary(
                op="mul",
                lhs=Term("ident", "a"),
                rhs=Term("ident", "b")
            ),
            rhs=Term("ident", "c")
        )
    ),
    (
        "a + b * c",
        Binary(
            op="add",
            lhs=Term("ident", "a"),
            rhs=Binary(
                op="mul",
                lhs=Term("ident", "b"),
                rhs=Term("ident", "c")
            )
        )
    ),
    (
        "-a + b",
        Binary(
            op="add",
            lhs=Unary(op="neg", arg=Term("ident", "a")),
            rhs=Term("ident", "b")
        )
    ),
    (
        "-a ^ b",
        Binary(
            op="pow",
            lhs=Unary(op="neg", arg=Term("ident", "a")),
            rhs=Term("ident", "b")
        )
    ),
    (
        "a ^ b ^ c",
        Binary(
            op="pow",
            lhs=Term("ident", "a"),
            rhs=Binary(
                op="pow",
                lhs=Term("ident", "b"),
                rhs=Term("ident", "c")
            )
        )
    ),
    (
        "-a!",
        Unary(op="neg", arg=Unary(op="fact", arg=Term("ident", "a")))
    ),
    (
        "(-a)!",
        Unary(op="fact", arg=Unary(op="neg", arg=Term("ident", "a")))
    ),
    (
        "--+a",
        Unary(
            op="neg",
            arg=Unary(
                op="neg",
                arg=Unary(op="pos", arg=Term("ident", "a"))
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
