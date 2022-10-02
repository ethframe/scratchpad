import os


def load_data(name: str) -> list[tuple[str, str]]:
    with open(os.path.join("data", name + ".txt"), "r") as fp:
        data = fp.read()
    tests: list[tuple[str, str]] = []
    for test in data.split("\n===\n"):
        source, result = test.split("\n---\n", 1)
        tests.append((source, result))
    return tests


EVALUATE_DATA = [
    ("1 2 + 3 +", 6),
    ("1 2 3 * +", 7),
    ("1 2 + 3 *", 9),
]
