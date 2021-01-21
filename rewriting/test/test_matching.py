from typing import List, Optional

import pytest

from rewriting.matching import build_pattern
from rewriting.terms import Func, Term, TermOpBuilder, Val, func, v, val

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
        term: Term, ops: List[TermOpBuilder],
        result: Optional[List[Term]]) -> None:
    assert build_pattern(ops).match(term) == result
