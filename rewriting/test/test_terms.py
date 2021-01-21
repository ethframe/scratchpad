from typing import List, Optional

import pytest

from rewriting.terms import (
    Func, MatchOpBuilder, Term, Val, build_pattern, func, v, val
)

TEST_DATA = [
    (Func("func", [Val("a"), Val("b")]), func("func", val("a"), val("b")), []),
    (
        Func("func", [Val("a"), Val("b")]),
        func("func", v("X"), val("b")),
        [Val("a")]
    ),
    (
        Func("func", [Val("a"), Val("b")]),
        func("func", v("X"), v("X")),
        None
    ),
    (
        Func("func", [Val("a"), Val("a")]),
        func("func", v("X"), v("X")),
        [Val("a")]
    ),
]


@pytest.mark.parametrize("term, ops, result", TEST_DATA)
def test_match(
        term: Term, ops: List[MatchOpBuilder],
        result: Optional[List[Term]]) -> None:
    assert build_pattern(ops).match(term) == result
