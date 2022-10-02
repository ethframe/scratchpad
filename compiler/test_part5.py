from unittest import TestCase

from data import load_data
from part5 import translate

TEST_DATA = load_data("part5")


class TestTranslate(TestCase):
    def test_translate(self) -> None:
        for source, result in TEST_DATA:
            with self.subTest(source=source, result=result):
                self.assertEqual(translate(source), result)
