from typing import Generic, Iterable, Iterator, TypeVar

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
V = TypeVar("V")


class _Pair(Generic[T, V]):
    __slots__ = "_fst", "_snd"

    def __init__(self, fst: T, snd: V):
        self._fst = fst
        self._snd = snd


class Chain(_Pair[Iterable[T_co], Iterable[T_co]], Iterable[T_co]):
    def __iter__(self) -> Iterator[T_co]:
        yield from self._fst
        yield from self._snd


class ChainL(_Pair[T_co, Iterable[T_co]], Iterable[T_co]):
    def __iter__(self) -> Iterator[T_co]:
        yield self._fst
        yield from self._snd


class ChainR(_Pair[Iterable[T_co], T_co], Iterable[T_co]):
    def __iter__(self) -> Iterator[T_co]:
        yield from self._fst
        yield self._snd
