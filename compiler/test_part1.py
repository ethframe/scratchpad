from unittest import TestCase

from data import EVALUATE_DATA
from part1 import evaluate


class TestEvaluate(TestCase):
    def test_evaluate(self) -> None:
        for source, result in EVALUATE_DATA:
            with self.subTest(source=source, result=result):
                self.assertEqual(evaluate(source), result)
