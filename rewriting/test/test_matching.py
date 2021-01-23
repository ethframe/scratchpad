from typing import List, Optional

import pytest

from rewriting.matching import PatternBuilder
from rewriting.terms import Func, Term, TermOp, Val, func, v, val

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


@pytest.mark.parametrize("term, pattern, result", TEST_DATA)
def test_match(
        term: Term, pattern: PatternBuilder[TermOp],
        result: Optional[List[Term]]) -> None:
    assert pattern.build().match(term) == result
