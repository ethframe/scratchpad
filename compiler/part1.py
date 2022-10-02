class EvaluationError(Exception):
    pass


def evaluate(source: str) -> int:
    stack: list[int] = []
    pos = 0
    while pos < len(source):
        c = source[pos]
        if c == "0":
            pos += 1
            if pos < len(source) and source[pos] != " ":
                raise EvaluationError()
            stack.append(0)
        elif "1" <= c and c <= "9":
            start = pos
            pos += 1
            while pos < len(source):
                c = source[pos]
                if c == " ":
                    break
                if c < "0" or c > "9":
                    raise EvaluationError()
                pos += 1
            value = int(source[start:pos])
            stack.append(value)
        elif c == " ":
            pos += 1
        elif c == "+":
            pos += 1
            if pos < len(source) and source[pos] != " ":
                raise EvaluationError()
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b)
        elif c == "*":
            pos += 1
            if pos < len(source) and source[pos] != " ":
                raise EvaluationError()
            b = stack.pop()
            a = stack.pop()
            stack.append(a * b)
        else:
            raise EvaluationError()
    return stack.pop()
