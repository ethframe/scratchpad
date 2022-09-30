from unittest import TestCase


def evaluate(source: str) -> int:
    stack: list[int] = []
    pos = 0
    while pos < len(source):
        c = source[pos]
        if "0" <= c and c <= "9":
            start = pos
            pos += 1
            while pos < len(source):
                c = source[pos]
                if c == " ":
                    break
                if c < "0" or c > "9":
                    raise RuntimeError()
                pos += 1
            value = int(source[start:pos])
            stack.append(value)
        elif c == " ":
            pos += 1
        elif c == "+":
            pos += 1
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b)
        elif c == "*":
            pos += 1
            b = stack.pop()
            a = stack.pop()
            stack.append(a * b)
        else:
            raise RuntimeError()
    return stack.pop()


class TestEvaluate(TestCase):
    def test_evaluate(self) -> None:
        for source, get_result in [
            ("1 2 + 3 +", 6),
            ("1 2 3 * +", 7),
            ("1 2 + 3 *", 9),
        ]:
            with self.subTest():
                self.assertEqual(evaluate(source), get_result)
