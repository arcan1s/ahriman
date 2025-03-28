#
# Copyright (c) 2021-2025 ahriman team.
#
# This file is part of ahriman
# (see https://github.com/arcan1s/ahriman).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass
from enum import ReprEnum
from types import SimpleNamespace
from typing import Generator, IO, Self

from ahriman.models.pkgbuild_patch import PkgbuildPatch


class PkgbuildToken(bytes, ReprEnum):

    Comment = b"#"
    Assignment = b"="
    SingleQuote = b"'"
    DoubleQuote = b"\""
    Space = b" "
    NewLine = b"\n"

    ParenthesisOpen = b"("
    ParenthesisClose = b")"

    FunctionStarts = b"function"
    FunctionDeclaration = b"()"
    BraceOpen = b"{"
    BraceClose = b"}"


@dataclass
class PkgbuildWord:

    word: bytes
    quote: bytes | None

    @property
    def closing(self) -> PkgbuildToken | None:
        if self.quote:
            return None
        match self.word:
            case PkgbuildToken.ParenthesisOpen:
                return PkgbuildToken.ParenthesisClose
            case PkgbuildToken.BraceOpen:
                return PkgbuildToken.BraceClose
        return None

    @property
    def original(self) -> bytes:
        quote = self.quote or b""
        return quote + self.word + quote

    def __bool__(self) -> bool:
        return bool(self.original)


class BytesPkgbuildParser(Iterator[PkgbuildPatch]):

    def __init__(self, stream: IO[bytes]) -> None:
        self._io = stream

    def _next(self, *, declaration: bool) -> bytes:
        while not (token := self._next_token(declaration=declaration)):
            continue
        return token

    def _next_token(self, *, declaration: bool) -> bytes:
        buffer = b""
        while word := self._next_word():
            match word:
                case PkgbuildWord(PkgbuildToken.Comment, None):
                    self._io.readline()

                case PkgbuildWord(PkgbuildToken.NewLine, None):
                    if declaration:
                        buffer = b""
                    return buffer

                case PkgbuildWord(PkgbuildToken.Assignment, None) if declaration:
                    return buffer

                case PkgbuildWord(PkgbuildToken.Space, None) if declaration:
                    if buffer.endswith(PkgbuildToken.FunctionDeclaration):
                        return buffer
                    buffer = b""
                    continue

                case PkgbuildWord(PkgbuildToken.Space, None):
                    return buffer

                case PkgbuildWord(PkgbuildToken.ParenthesisOpen, None):
                    buffer += PkgbuildToken.ParenthesisOpen
                    buffer += b"".join(self._next_words_until(PkgbuildWord(PkgbuildToken.ParenthesisClose, None)))

                case PkgbuildWord(PkgbuildToken.BraceOpen, None):
                    buffer += PkgbuildToken.BraceOpen
                    buffer += b"".join(self._next_words_until(PkgbuildWord(PkgbuildToken.BraceClose, None)))

                case PkgbuildWord(token, _):
                    buffer += token

        raise StopIteration

    def _next_word(self) -> PkgbuildWord:
        # pass SimpleNamespace as an argument to implement side effects
        def generator(quote: SimpleNamespace) -> Generator[bytes, None, None]:
            while token := self._io.read(1):
                match token:
                    case (PkgbuildToken.SingleQuote | PkgbuildToken.DoubleQuote) if quote.open is None:
                        quote.open = token
                    case closing_quote if closing_quote == quote.open:
                        return
                    case part:
                        yield part
                        if quote.open is None:
                            return

            if quote.open is not None:
                raise ValueError("No closing quotation")

        open_quote = SimpleNamespace(open=None)
        value = b"".join(generator(open_quote))

        return PkgbuildWord(value, open_quote.open)

    def _next_words_until(self, ending: PkgbuildWord) -> Generator[bytes, None, None]:
        braces = defaultdict(int)
        while element := self._next_word():
            yield element.original
            match element:
                case PkgbuildWord(token, None) if braces[token] > 0:
                    braces[token] -= 1
                case with_closure if (closing := with_closure.closing) is not None:
                    braces[closing] += 1
                case _ if element == ending:
                    return

        if any(brace for brace in braces.values() if brace > 0):
            raise ValueError("Unclosed parenthesis and/or braces found")
        raise ValueError(f"No matching ending element {ending.word} found")

    def parse(self) -> Generator[PkgbuildPatch, None, None]:
        """
        parse source stream and yield parsed entries

        Yields:
            PkgbuildPatch: extracted a PKGBUILD node
        """
        yield from self

    def __iter__(self) -> Self:
        """
        base iterator method

        Returns:
            Self: iterator instance
        """
        return self

    def __next__(self) -> PkgbuildPatch:
        key = self._next(declaration=True)
        value = self._next(declaration=False)

        return PkgbuildPatch(key.decode(encoding="utf8"), value.decode(encoding="utf8"))
