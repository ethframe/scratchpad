from typing import Iterable, Iterator, NamedTuple, Pattern


class Token(NamedTuple):
    kind: str
    value: str


def split_tokens(src: str, spec: Pattern[str], eof: Token) -> Iterator[Token]:
    pos = 0
    src_len = len(src)
    while pos < src_len:
        match = spec.match(src, pos=pos)
        if match is None:
            raise ValueError()
        kind = match.lastgroup
        if kind is not None:
            yield Token(kind, match.group(kind))
        pos = match.end()
    yield eof


class Lexer:
    def __init__(self, tokens: Iterable[Token]):
        self._tokens = iter(tokens)
        self._token = next(self._tokens)

    def peek(self) -> Token:
        return self._token

    def advance(self) -> Token:
        token = self._token
        self._token = next(self._tokens)
        return token
