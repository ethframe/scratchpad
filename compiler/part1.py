class EvaluationError(Exception):
    pass


def evaluate(source: str) -> int:
    stack: list[int] = []
    pos = 0
    while pos < len(source):
        c = source[pos]
        if c == " ":
            pos += 1
        elif "0" <= c and c <= "9":
            start = pos
            pos += 1
            while pos < len(source):
                c = source[pos]
                if c < "0" or c > "9":
                    break
                pos += 1
            value = int(source[start:pos])
            stack.append(value)
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
            raise EvaluationError()
    return stack.pop()
