from unittest import TestCase

from data import load_data
from part6 import translate

TEST_DATA = load_data("part4")


class TestTranslate(TestCase):
    def test_translate(self) -> None:
        for source, result in TEST_DATA:
            with self.subTest(source=source, result=result):
                self.assertEqual(translate(source), result)
