from typing import Iterable, Iterator, TypeVar

T = TypeVar("T")


def batch(iterable: Iterable[T], size: int) -> Iterator[list[T]]:
    buf: list[T] = []
    for item in iterable:
        buf.append(item)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf
