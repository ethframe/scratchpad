from unittest import TestCase

from data import EVALUATE_DATA, load_data
from part4 import evaluate, translate

TEST_DATA = load_data("part4")


class TestEvaluate(TestCase):
    def test_evaluate(self) -> None:
        for source, result in EVALUATE_DATA:
            with self.subTest(source=source, result=result):
                self.assertEqual(evaluate(source), result)


class TestTranslate(TestCase):
    def test_translate(self) -> None:
        for source, result in TEST_DATA:
            with self.subTest(source=source, result=result):
                self.assertEqual(translate(source), result)
