import pytest
from pretty import P, Pretty
from textwrap import dedent


def binop(left: str, op: str, right: str) -> Pretty:
    return P.group(P.nest(2, P.group(P.text(left).sp().text(op)).sp()
                              .text(right)))


def if_then(cond: Pretty, expr1: Pretty, expr2: Pretty) -> Pretty:
    return P.group(P.group(P.nest(2, P.text("if").sp().then(cond))).sp()
                    .group(P.nest(2, P.text("then").sp().then(expr1))).sp()
                    .group(P.nest(2, P.text("else").sp().then(expr2))))


@pytest.fixture(scope="module")
def strictly_pretty_example() -> Pretty:
    cond = binop("a", "==", "b")
    expr1 = binop("a", "<<", "2")
    expr2 = binop("a", "+", "b")

    return if_then(cond, expr1, expr2)


STRICTLY_PRETTY_DATA: list[tuple[int, str]] = [
    (32, "if a == b then a << 2 else a + b"),
    (15, """\
          if a == b
          then a << 2
          else a + b"""),
    (10, """\
          if a == b
          then
            a << 2
          else a + b"""),
    (8, """\
         if
           a == b
         then
           a << 2
         else
           a + b"""),
    (7, """\
          if
            a ==
              b
          then
            a <<
              2
          else
            a + b"""),
    (6, """\
         if
           a ==
             b
         then
           a <<
             2
         else
           a +
             b"""),
]


@pytest.mark.parametrize("width, expected", STRICTLY_PRETTY_DATA)
def test_strictly_pretty(
        strictly_pretty_example: Pretty, width: int, expected: str) -> None:
    assert strictly_pretty_example.to_string(width) == dedent(expected)
