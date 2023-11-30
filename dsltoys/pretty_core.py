from abc import ABC, abstractmethod
from io import TextIOBase


class Doc(ABC):
    @abstractmethod
    def get_width(self) -> int: ...
    @abstractmethod
    def format(self, indent: int, flat: bool, fmt: "Formatter") -> None: ...


class DocCons(Doc):
    def __init__(self, fst: Doc, snd: Doc):
        self._fst = fst
        self._snd = snd
        self._width = self._fst.get_width() + self._snd.get_width()

    def get_width(self) -> int:
        return self._width

    def format(self, indent: int, flat: bool, fmt: "Formatter") -> None:
        fmt.enqueue(indent, flat, self._snd)
        fmt.enqueue(indent, flat, self._fst)


class DocText(Doc):
    def __init__(self, text: str):
        self._text = text

    def get_width(self) -> int:
        return len(self._text)

    def format(self, indent: int, flat: bool, fmt: "Formatter") -> None:
        fmt.text(self._text)


class DocNest(Doc):
    def __init__(self, indent: int, nested: Doc):
        self._indent = indent
        self._nested = nested

    def get_width(self) -> int:
        return self._nested.get_width()

    def format(self, indent: int, flat: bool, fmt: "Formatter") -> None:
        fmt.enqueue(indent + self._indent, flat, self._nested)


class DocBreak(Doc):
    def __init__(self, value: str):
        self._value = value

    def get_width(self) -> int:
        return len(self._value)

    def format(self, indent: int, flat: bool, fmt: "Formatter") -> None:
        if flat:
            fmt.text(self._value)
        else:
            fmt.line(indent)


class DocGroup(Doc):
    def __init__(self, doc: Doc):
        self._doc = doc

    def get_width(self) -> int:
        return self._doc.get_width()

    def format(self, indent: int, flat: bool, fmt: "Formatter") -> None:
        fmt.enqueue(indent, fmt.fits(self._doc), self._doc)


class Formatter:
    def __init__(self, stream: TextIOBase, width: int):
        self._stream = stream
        self._width = width
        self._current = 0
        self._newlines = 0
        self._indent = 0
        self._stack: list[tuple[int, bool, Doc]] = []

    def text(self, text: str) -> None:
        if self._newlines != 0:
            self._stream.write("\n" * self._newlines)
            self._newlines = 0
        if self._indent != 0:
            self._stream.write(" " * self._indent)
            self._indent = 0
        self._stream.write(text)
        self._current += len(text)

    def line(self, indent: int) -> None:
        self._newlines += 1
        self._indent = indent
        self._current = indent

    def fits(self, doc: Doc) -> bool:
        return self._width >= self._current + doc.get_width()

    def enqueue(self, indent: int, flat: bool, doc: Doc) -> None:
        self._stack.append((indent, flat, doc))

    def format(self, doc: Doc) -> None:
        self._stack.append((0, True, doc))
        while len(self._stack) != 0:
            indent, flat, doc = self._stack.pop()
            doc.format(indent, flat, self)
        if self._newlines != 0:
            self._stream.write("\n")
            self._newlines -= 1
