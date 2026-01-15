#
# Copyright (c) 2021-2026 ahriman team.
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

from collections.abc import Iterator
from enum import StrEnum
from typing import IO

from ahriman.core.exceptions import PkgbuildParserError
from ahriman.models.pkgbuild_patch import PkgbuildPatch


class PkgbuildToken(StrEnum):
    """
    well-known tokens dictionary

    Attributes:
        ArrayEnds(PkgbuildToken): array ends token
        ArrayStarts(PkgbuildToken): array starts token
        Comma(PkgbuildToken): comma token
        Comment(PkgbuildToken): comment token
        FunctionDeclaration(PkgbuildToken): function declaration token
        FunctionEnds(PkgbuildToken): function ends token
        FunctionStarts(PkgbuildToken): function starts token
        NewLine(PkgbuildToken): new line token
    """

    ArrayStarts = "("
    ArrayEnds = ")"

    Comma = ","

    Comment = "#"

    FunctionDeclaration = "()"
    FunctionStarts = "{"
    FunctionEnds = "}"

    NewLine = "\n"


class PkgbuildParser(shlex.shlex):
    """
    simple pkgbuild reader implementation in pure python, because others suck.

    What is it:

    #. Simple PKGBUILD parser written in python.
    #. No shell execution, so it is free from random shell attacks.
    #. Able to parse simple constructions (assignments, comments, functions, arrays).

    What it is not:

    #. Fully functional shell parser.
    #. Shell executor.
    #. No parameter expansion.

    For more details what does it support, please, consult with the test cases.

    Examples:
        This class is heavily based on :mod:`shlex` parser, but instead of strings operates with the
        :class:`ahriman.models.pkgbuild_patch.PkgbuildPatch` objects. The main way to use it is to call :func:`parse()`
        function and collect parsed objects, e.g.::

            >>> parser = PkgbuildParser(StringIO("input string"))
            >>> for patch in parser.parse():
            >>>     print(f"{patch.key} = {patch.value}")

        It doesn't store the state of the fields (but operates with the :mod:`shlex` parser state), so no shell
        post-processing is performed (e.g. variable substitution).
    """

    _ARRAY_ASSIGNMENT = re.compile(r"^(?P<key>\w+)=$")
    # in addition to usual assignment, functions can have dash
    _FUNCTION_DECLARATION = re.compile(r"^(?P<key>[\w-]+)$")
    _STRING_ASSIGNMENT = re.compile(r"^(?P<key>\w+)=(?P<value>.+)$")

    def __init__(self, stream: IO[str]) -> None:
        """
        Args:
            stream(IO[str]): input stream containing PKGBUILD content
        """
        shlex.shlex.__init__(self, stream, posix=True, punctuation_chars=True)
        self._io = stream  # direct access without type casting

        # ignore substitution and extend bash symbols
        self.wordchars += "${}#:+-@!"
        # in case of default behaviour, it will ignore, for example, segment part of url outside of quotes
        self.commenters = ""

    @staticmethod
    def _expand_array(array: list[str]) -> list[str]:
        """
        bash array expansion simulator. It takes raw array and tries to expand constructions like
        ``(first prefix-{mid1,mid2}-suffix last)`` into ``(first, prefix-mid1-suffix prefix-mid2-suffix last)``

        Args:
            array(list[str]): input array

        Returns:
            list[str]: either source array or expanded array if possible

        Raises:
            PkgbuildParserError: if there are errors in parser
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

                # we have already got prefix string, so we are in progress of expansion
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
            raise PkgbuildParserError("error in array expansion", array)

        return result

    def _is_escaped(self) -> bool:
        """
        check if the last element was quoted. ``shlex.shlex`` parser doesn't provide information about was the token
        quoted or not, thus there is no difference between "'#'" (sharp in quotes) and "#" (sharp without quotes). This
        method simply rolls back to the last non-space character and check if it is a quotation mark

        Returns:
            bool: ``True`` if the previous element of the stream is a quote or escaped and ``False`` otherwise
        """
        current_position = self._io.tell()

        last_char = penultimate_char = None
        index = current_position - 1
        while index > 0:
            index, last_char = self._read_last(index)
            if last_char.isspace():
                index -= 1
                continue

            if index > 1:
                _, penultimate_char = self._read_last(index - 1)

            break

        self._io.seek(current_position)  # reset position of the stream
        is_quoted = last_char is not None and last_char in self.quotes
        is_escaped = penultimate_char is not None and penultimate_char in self.escape

        return is_quoted or is_escaped

    def _parse_array(self) -> list[str]:
        """
        parse array from the PKGBUILD. This method will extract tokens from parser until it matches closing array,
        modifying source parser state

        Returns:
            list[str]: extracted arrays elements

        Raises:
            PkgbuildParserError: if array is not closed
        """
        def extract() -> Iterator[str]:
            while token := self.get_token():
                match token:
                    case _ if self._is_escaped():
                        pass
                    case PkgbuildToken.ArrayEnds:
                        break
                    case comment if comment.startswith(PkgbuildToken.Comment):
                        self._read_comment()
                        continue

                yield token

            if token != PkgbuildToken.ArrayEnds:
                raise PkgbuildParserError("no closing array bracket found")

        return self._expand_array(list(extract()))

    def _parse_function(self) -> str:
        """
        parse function from the PKGBUILD. This method will extract tokens from parser until it matches closing function,
        modifying source parser state. Instead of trying to combine tokens together, it uses positions of the file
        and reads content again in this range

        Returns:
            str: function body

        Raises:
            PkgbuildParserError: if function body wasn't found or parser input stream doesn't support position reading
        """
        # find start and end positions
        start_position = end_position = -1
        counter = 0  # simple processing of the inner "{" and "}"
        for token in self:
            match token:
                case _ if self._is_escaped():
                    continue
                case PkgbuildToken.FunctionStarts:
                    if counter == 0:
                        start_position = self._io.tell() - 1
                    counter += 1
                case PkgbuildToken.FunctionEnds:
                    end_position = self._io.tell()
                    if self.state != self.eof:  # type: ignore[attr-defined]
                        end_position -= 1  # if we are not at the end of the file, position is _after_ the token
                    counter -= 1
                    if counter == 0:
                        break
                case comment if comment.startswith(PkgbuildToken.Comment):
                    self._read_comment()

        if not 0 < start_position < end_position:
            raise PkgbuildParserError("function body wasn't found")

        # read the specified interval from source stream
        self._io.seek(start_position - 1)  # start from the previous symbol
        # we cannot use :func:`read()` here, because it reads characters, not bytes
        content = ""
        while self._io.tell() != end_position and (next_char := self._io.read(1)):
            content += next_char

        # special case of the end of file
        if self.state == self.eof:  # type: ignore[attr-defined]
            content += self._io.read(1)

        return content

    def _parse_token(self, token: str) -> Iterator[PkgbuildPatch]:
        """
        parse single token to the PKGBUILD field

        Args:
            token(str): current token

        Yields:
            PkgbuildPatch: extracted a PKGBUILD node
        """
        # simple assignment rule
        if m := self._STRING_ASSIGNMENT.match(token):
            key = m.group("key")
            value = m.group("value")
            yield PkgbuildPatch(key, value)
            return

        if token.startswith(PkgbuildToken.Comment):
            self._read_comment()
            return

        match self.get_token():
            # array processing. Arrays will be sent as "key=", "(", values, ")"
            case PkgbuildToken.ArrayStarts if m := self._ARRAY_ASSIGNMENT.match(token):
                key = m.group("key")
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

    def _read_comment(self) -> None:
        """
        read comment from the current position. This method doesn't check comment itself, just read the stream
        until the comment line ends
        """
        _, last_symbol = self._read_last()
        if last_symbol != PkgbuildToken.NewLine:
            self.instream.readline()

    def _read_last(self, initial_index: int | None = None) -> tuple[int, str]:
        """
        wrapper around read to read the last symbol from the input stream. This method is designed to process UTF-8
        symbols correctly. This method does not reset current stream position

        Args:
            initial_index(int | None, optional): initial index to start reading from. If none set, the previous position
                will be used (Default value = None)

        Returns:
            tuple[int, str]: last symbol and its position in the stream

        Raises:
            PkgbuildParserError: in case if stream reached starting position, but no valid symbols were found
        """
        if initial_index is None:
            initial_index = self._io.tell() - 1
        if initial_index < 0:
            raise PkgbuildParserError("stream is on starting position")
        self._io.seek(initial_index)

        while (position := self._io.tell()) > 0:
            try:
                return position, self._io.read(1)
            except UnicodeDecodeError:
                self._io.seek(position - 1)

        raise PkgbuildParserError("reached starting position, no valid symbols found")

    def parse(self) -> Iterator[PkgbuildPatch]:
        """
        parse source stream and yield parsed entries

        Yields:
            PkgbuildPatch: extracted a PKGBUILD node
        """
        for token in self:
            yield from self._parse_token(token)
