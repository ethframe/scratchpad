from io import StringIO

from pretty_core import (
    Doc, DocBreak, DocCons, DocGroup, DocNest, DocText, Formatter
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
        return self._cons(DocBreak(" "))

    def br(self, text: str) -> "Pretty":
        return self._cons(DocBreak(text))

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


class P:
    @staticmethod
    def text(text: str) -> Pretty:
        return Pretty(DocText(text))

    @staticmethod
    def group(doc: Pretty) -> Pretty:
        return doc.wrap_in_group()

    @staticmethod
    def nest(indent: int, nested: Pretty) -> Pretty:
        return nested.wrap_in_nest(indent)
