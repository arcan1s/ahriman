#
# Copyright (c) 2021-2024 ahriman team.
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
import itertools
import re
import shlex

from collections.abc import Generator
from enum import StrEnum
from typing import IO

from ahriman.models.pkgbuild_patch import PkgbuildPatch


class PkgbuildToken(StrEnum):
    """
    well-known tokens dictionary

    Attributes:
        ArrayEnds(PkgbuildToken): (class attribute) array ends token
        ArrayStarts(PkgbuildToken): (class attribute) array starts token
        Comma(PkgbuildToken): (class attribute) comma token
        Comment(PkgbuildToken): (class attribute) comment token
        FunctionDeclaration(PkgbuildToken): (class attribute) function declaration token
        FunctionEnds(PkgbuildToken): (class attribute) function ends token
        FunctionStarts(PkgbuildToken): (class attribute) function starts token
    """

    ArrayStarts = "("
    ArrayEnds = ")"

    Comma = ","

    Comment = "#"

    FunctionDeclaration = "()"
    FunctionStarts = "{"
    FunctionEnds = "}"


class PkgbuildParser(shlex.shlex):
    """
    simple pkgbuild reader implementation in pure python, because others suck
    """

    _ARRAY_ASSIGNMENT = re.compile(r"^(?P<key>\w+)=$")
    # in addition to usual assignment, functions can have dash
    _FUNCTION_DECLARATION = re.compile(r"^(?P<key>[\w-]+)$")
    _STRING_ASSIGNMENT = re.compile(r"^(?P<key>\w+)=(?P<value>.+)$")

    def __init__(self, stream: IO[str]) -> None:
        """
        default constructor

        Args:
            stream(IO[str]): input stream containing PKGBUILD content
        """
        shlex.shlex.__init__(self, stream, posix=True, punctuation_chars=True)
        self._io = stream  # direct access without type casting

        # ignore substitution and extend bash symbols
        self.wordchars += "${}#:+-@"
        # in case of default behaviour, it will ignore, for example, segment part of url outside of quotes
        self.commenters = ""

    @staticmethod
    def _expand_array(array: list[str]) -> list[str]:
        """
        bash array expansion simulator. It takes raw parsed array and tries to expand constructions like
        ``(first prefix-{mid1,mid2}-suffix last)`` into ``(first, prefix-mid1-suffix prefix-mid2-suffix last)``

        Args:
            array(list[str]): input array

        Returns:
            list[str]: either source array or expanded array if possible

        Raises:
            ValueError: if there are errors in parser
        """
        # we are using comma as marker for expansion (if any)
        if PkgbuildToken.Comma not in array:
            return array
        # again sanity check, for expansion there are at least 3 elements (first, last and comma)
        if len(array) < 3:
            return array

        result = []
        buffer, prefix = [], None

        for index, (first, second) in enumerate(itertools.pairwise(array)):
            match (first, second):
                # in this case we check if expansion should be started
                # this condition matches "prefix{first", ","
                case (_, PkgbuildToken.Comma) if PkgbuildToken.FunctionStarts in first:
                    prefix, part = first.rsplit(PkgbuildToken.FunctionStarts, maxsplit=1)
                    buffer.append(f"{prefix}{part}")

                # the last element case, it matches either ",", "last}" or ",", "last}suffix"
                # in case if there is suffix, it must be appended to all list elements
                case (PkgbuildToken.Comma, _) if prefix is not None and PkgbuildToken.FunctionEnds in second:
                    part, suffix = second.rsplit(PkgbuildToken.FunctionEnds, maxsplit=1)
                    buffer.append(f"{prefix}{part}")
                    result.extend([f"{part}{suffix}" for part in buffer])
                    # reset state
                    buffer, prefix = [], None

                # we have already prefix string, so we are in progress of expansion
                # we always operate the last element, so this matches ",", "next"
                case (PkgbuildToken.Comma, _) if prefix is not None:
                    buffer.append(f"{prefix}{second}")

                # exactly first element of the list
                case (_, _) if prefix is None and index == 0:
                    result.append(first)

                # any next normal element
                case (_, _) if prefix is None:
                    result.append(second)

        # small sanity check
        if prefix is not None:
            raise ValueError(f"Could not expand `{array}` as array")

        return result

    def _parse_array(self) -> list[str]:
        """
        parse array from the PKGBUILD. This method will extract tokens from parser until it matches closing array,
        modifying source parser state

        Returns:
            list[str]: extracted arrays elements

        Raises:
            ValueError: if array is not closed
        """
        def extract() -> Generator[str, None, None]:
            while token := self.get_token():
                if token == PkgbuildToken.ArrayEnds:
                    break
                if token == PkgbuildToken.Comment:
                    self.instream.readline()
                    continue
                yield token

            if token != PkgbuildToken.ArrayEnds:
                raise ValueError("No closing array bracket found")

        return self._expand_array(list(extract()))

    def _parse_function(self) -> str:
        """
        parse function from the PKGBUILD. This method will extract tokens from parser until it matches closing function,
        modifying source parser state. Instead of trying to combine tokens together, it uses positions of the file
        and read content again in this range

        Returns:
            str: function body

        Raises:
            ValueError: if function body wasn't found or parser input stream doesn't support position reading
        """
        # find start and end positions
        start_position, end_position = -1, -1
        while token := self.get_token():
            match token:
                case PkgbuildToken.FunctionStarts:
                    start_position = self._io.tell() - 1
                case PkgbuildToken.FunctionEnds:
                    end_position = self._io.tell()
                    break

        if not 0 < start_position < end_position:
            raise ValueError("Function body wasn't found")

        # read the specified interval from source stream
        self._io.seek(start_position - 1)  # start from the previous symbol
        content = self._io.read(end_position - start_position)

        return content

    def _parse_token(self, token: str) -> Generator[PkgbuildPatch, None, None]:
        """
        parse single token to the PKGBUILD field

        Args:
            token(str): current token

        Yields:
            PkgbuildPatch: extracted a PKGBUILD node
        """
        # simple assignment rule
        if (match := self._STRING_ASSIGNMENT.match(token)) is not None:
            key = match.group("key")
            value = match.group("value")
            yield PkgbuildPatch(key, value)
            return

        if token == PkgbuildToken.Comment:
            self.instream.readline()
            return

        match self.get_token():
            # array processing. Arrays will be sent as "key=", "(", values, ")"
            case PkgbuildToken.ArrayStarts if (match := self._ARRAY_ASSIGNMENT.match(token)) is not None:
                key = match.group("key")
                value = self._parse_array()
                yield PkgbuildPatch(key, value)

            # functions processing. Function will be sent as "name", "()", "{", body, "}"
            case PkgbuildToken.FunctionDeclaration if self._FUNCTION_DECLARATION.match(token):
                key = f"{token}{PkgbuildToken.FunctionDeclaration}"
                value = self._parse_function()
                yield PkgbuildPatch(key, value)  # this is not mistake, assign to token without ()

            # special function case, where "(" and ")" are separated tokens, e.g. "pkgver ( )"
            case PkgbuildToken.ArrayStarts if self._FUNCTION_DECLARATION.match(token):
                next_token = self.get_token()
                if next_token == PkgbuildToken.ArrayEnds:  # replace closing bracket with "()"
                    next_token = PkgbuildToken.FunctionDeclaration
                self.push_token(next_token)  # type: ignore[arg-type]
                yield from self._parse_token(token)

            # some random token received without continuation, lets guess it is empty assignment (i.e. key=)
            case other if other is not None:
                yield from self._parse_token(other)

    def parse(self) -> Generator[PkgbuildPatch, None, None]:
        """
        parse source stream and yield parsed entries

        Yields:
            PkgbuildPatch: extracted a PKGBUILD node
        """
        for token in self:
            yield from self._parse_token(token)
