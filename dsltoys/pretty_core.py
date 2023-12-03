from abc import ABC, abstractmethod
from io import TextIOBase


class Doc(ABC):
    @abstractmethod
    def fits(self, flat: bool, fit: "Fitter") -> None: ...
    @abstractmethod
    def format(self, indent: int, flat: bool, fmt: "Formatter") -> None: ...


class DocCons(Doc):
    def __init__(self, fst: Doc, snd: Doc):
        self._fst = fst
        self._snd = snd

    def fits(self, flat: bool, fit: "Fitter") -> None:
        fit.enqueue(flat, self._snd)
        fit.enqueue(flat, self._fst)

    def format(self, indent: int, flat: bool, fmt: "Formatter") -> None:
        fmt.enqueue(indent, flat, self._snd)
        fmt.enqueue(indent, flat, self._fst)


class DocText(Doc):
    def __init__(self, text: str):
        self._text = text

    def fits(self, flat: bool, fit: "Fitter") -> None:
        fit.text(self._text)

    def format(self, indent: int, flat: bool, fmt: "Formatter") -> None:
        fmt.text(self._text)


class DocNest(Doc):
    def __init__(self, indent: int, nested: Doc):
        self._indent = indent
        self._nested = nested

    def fits(self, flat: bool, fit: "Fitter") -> None:
        fit.enqueue(flat, self._nested)

    def format(self, indent: int, flat: bool, fmt: "Formatter") -> None:
        fmt.enqueue(indent + self._indent, flat, self._nested)


class DocBreak(Doc):
    def __init__(self, value: str):
        self._value = value

    def fits(self, flat: bool, fit: "Fitter") -> None:
        if flat:
            fit.text(self._value)
        else:
            fit.line()

    def format(self, indent: int, flat: bool, fmt: "Formatter") -> None:
        if flat:
            fmt.text(self._value)
        else:
            fmt.line(indent)


class DocGroup(Doc):
    def __init__(self, doc: Doc):
        self._doc = doc

    def fits(self, flat: bool, fit: "Fitter") -> None:
        fit.enqueue(True, self._doc)

    def format(self, indent: int, flat: bool, fmt: "Formatter") -> None:
        fmt.enqueue(indent, fmt.fits(self._doc), self._doc)


class Fitter:
    def __init__(self, width: int) -> None:
        self._width = width
        self._newline = False
        self._stack: list[tuple[bool, Doc]] = []

    def enqueue(self, flat: bool, doc: Doc) -> None:
        self._stack.append((flat, doc))

    def text(self, text: str) -> None:
        self._width -= len(text)

    def line(self) -> None:
        self._newline = True

    def fits(self, doc: Doc, rest: list[tuple[int, bool, Doc]]) -> bool:
        next = len(rest)
        self._stack.append((True, doc))
        while len(self._stack) != 0:
            flat, doc = self._stack.pop()
            doc.fits(flat, self)
            if self._width < 0:
                return False
            if self._newline:
                return True
            if len(self._stack) == 0 and next != 0:
                next -= 1
                _, flat, doc = rest[next]
                self._stack.append((flat, doc))
        return True


class Formatter:
    def __init__(self, stream: TextIOBase, width: int):
        self._stream = stream
        self._width = width
        self._current = 0
        self._indent = 0
        self._stack: list[tuple[int, bool, Doc]] = []

    def text(self, text: str) -> None:
        if self._indent > 0:
            self._stream.write(" " * self._indent)
            self._indent = 0
        self._stream.write(text)
        self._current += len(text)

    def line(self, indent: int) -> None:
        self._stream.write("\n")
        self._current = indent
        self._indent = indent

    def fits(self, doc: Doc) -> bool:
        return Fitter(self._width - self._current).fits(doc, self._stack)

    def enqueue(self, indent: int, flat: bool, doc: Doc) -> None:
        self._stack.append((indent, flat, doc))

    def format(self, doc: Doc) -> None:
        self._stack.append((0, True, doc))
        while len(self._stack) != 0:
            indent, flat, doc = self._stack.pop()
            doc.format(indent, flat, self)
