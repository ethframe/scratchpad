from io import StringIO

from pretty_core import (
    Doc, DocBreak, DocCons, DocGroup, DocNest, DocNil, DocText, Formatter
)


class Pretty:
    def __init__(self, doc: Doc):
        self._doc = doc

    def _cons(self, snd: Doc) -> "Pretty":
        return Pretty(DocCons(self._doc, snd))

    def then(self, snd: "Pretty") -> "Pretty":
        return self._cons(snd._doc)

    def text(self, text: str) -> "Pretty":
        return self._cons(DocText(text))

    def sp(self) -> "Pretty":
        return self._cons(DocBreak(" ", ""))

    def br(self, text: str, break_: str) -> "Pretty":
        return self._cons(DocBreak(text, break_))

    def nl(self) -> "Pretty":
        return self._cons(DocBreak(None, ""))

    def group(self, doc: "Pretty") -> "Pretty":
        return self._cons(DocGroup(doc._doc))

    def nest(self, indent: int, nested: "Pretty") -> "Pretty":
        return self._cons(DocNest(indent, nested._doc))

    def wrap_in_group(self) -> "Pretty":
        return Pretty(DocGroup(self._doc))

    def wrap_in_nest(self, indent: int) -> "Pretty":
        return Pretty(DocNest(indent, self._doc))

    def to_string(self, width: int) -> str:
        stream = StringIO()
        Formatter(stream, width).format(self._doc)
        return stream.getvalue()


P = Pretty(DocNil())
