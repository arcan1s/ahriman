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
import re
import shlex

from collections.abc import Generator, Iterator, Mapping
from dataclasses import dataclass
from enum import StrEnum
from io import StringIO
from pathlib import Path
from typing import IO, Self, TypeVar, cast

from ahriman.models.pkgbuild_patch import PkgbuildPatch


T = TypeVar("T", str, list[str])
U = TypeVar("U", str, list[str], None)


class PkgbuildToken(StrEnum):
    """
    well-known tokens dictionary

    Attributes:
        ArrayStarts(PkgbuildToken): (class attribute) array starts token
        ArrayEnds(PkgbuildToken): (class attribute) array ends token
        FunctionDeclaration(PkgbuildToken): (class attribute) function declaration token
        FunctionStarts(PkgbuildToken): (class attribute) function starts token
        FunctionEnds(PkgbuildToken): (class attribute) function ends token
    """

    ArrayStarts = "("
    ArrayEnds = ")"

    FunctionDeclaration = "()"
    FunctionStarts = "{"
    FunctionEnds = "}"


@dataclass(frozen=True)
class Pkgbuild(Mapping[str, str | list[str]]):
    """
    simple pkgbuild reader implementation in pure python, because others sucks

    Attributes:
        fields(dict[str, PkgbuildPatch]): PKGBUILD fields
    """

    fields: dict[str, PkgbuildPatch]

    _ARRAY_ASSIGNMENT = re.compile(r"^(?P<key>\w+)=$")
    _STRING_ASSIGNMENT = re.compile(r"^(?P<key>\w+)=(?P<value>.+)$")
    # in addition, functions can have dash to usual assignment
    _FUNCTION_DECLARATION = re.compile(r"^(?P<key>[\w-]+)$")

    @property
    def variables(self) -> dict[str, str]:
        """
        list of variables defined and (maybe) used in this PKGBUILD

        Returns:
            dict[str, str]: map of variable name to its value. The value will be included here in case if it presented
            in the internal dictionary, it is not a function and the value has string type
        """
        return {
            key: value.value
            for key, value in self.fields.items()
            if not value.is_function and isinstance(value.value, str)
        }

    @classmethod
    def from_file(cls, path: Path) -> Self:
        """
        parse PKGBUILD from the file

        Args:
            path(Path): path to the PKGBUILD file

        Returns:
            Self: constructed instance of self
        """
        with path.open() as input_file:
            return cls.from_io(input_file)

    @classmethod
    def from_io(cls, stream: IO[str]) -> Self:
        """
        parse PKGBUILD from input stream

        Args:
            stream: IO[str]: input stream containing PKGBUILD content

        Returns:
            Self: constructed instance of self
        """
        fields = {}

        parser = shlex.shlex(stream, posix=True, punctuation_chars=True)
        while token := parser.get_token():
            try:
                key, value = cls._parse_token(token, parser)
                fields[key] = value
            except StopIteration:
                break

        return cls(fields)

    @staticmethod
    def _parse_array(parser: shlex.shlex) -> list[str]:
        """
        parse array from the PKGBUILD. This method will extract tokens from parser until it matches closing array,
        modifying source parser state

        Args:
            parser(shlex.shlex): shell parser instance

        Returns:
            list[str]: extracted arrays elements

        Raises:
            ValueError: if array is not closed
        """
        def extract() -> Generator[str, None, None]:
            while token := parser.get_token():
                if token == PkgbuildToken.ArrayEnds:
                    break
                yield token

            if token != PkgbuildToken.ArrayEnds:
                raise ValueError("No closing array bracket found")

        return list(extract())

    @staticmethod
    def _parse_function(parser: shlex.shlex) -> str:
        """
        parse function from the PKGBUILD. This method will extract tokens from parser until it matches closing function,
        modifying source parser state. Instead of trying to combine tokens together, it uses positions of the file
        and read content again in this range

        Args:
            parser(shlex.shlex): shell parser instance

        Returns:
            str: function body

        Raises:
            ValueError: if function body wasn't found or parser input stream doesn't support position reading
        """
        io: IO[str] = parser.instream  # type: ignore[assignment]

        # find start and end positions
        start_position, end_position = -1, -1
        while token := parser.get_token():
            match token:
                case PkgbuildToken.FunctionStarts:
                    start_position = io.tell()
                case PkgbuildToken.FunctionEnds:
                    end_position = io.tell()
                    break

        if not 0 < start_position < end_position:
            raise ValueError("Function body wasn't found")

        # read the specified interval from source stream
        io.seek(start_position - 1)  # start from the previous symbol ({)
        content = io.read(end_position - start_position + 1)

        return content

    @staticmethod
    def _parse_token(token: str, parser: shlex.shlex) -> tuple[str, PkgbuildPatch]:
        """
        parse single token to the PKGBUILD field

        Args:
            token(str): current token
            parser(shlex.shlex): shell parser instance

        Returns:
            tuple[str, PkgbuildPatch]: extracted a pair of key and its value

        Raises:
            StopIteration: if iteration reaches the end of the file'
        """
        # simple assignment rule
        if (match := Pkgbuild._STRING_ASSIGNMENT.match(token)) is not None:
            key = match.group("key")
            value = match.group("value")
            return key, PkgbuildPatch(key, value)

        match parser.get_token():
            # array processing. Arrays will be sent as "key=", "(", values, ")"
            case PkgbuildToken.ArrayStarts if (match := Pkgbuild._ARRAY_ASSIGNMENT.match(token)) is not None:
                key = match.group("key")
                value = Pkgbuild._parse_array(parser)
                return key, PkgbuildPatch(key, value)

            # functions processing. Function will be sent as "name", "()", "{", body, "}"
            case PkgbuildToken.FunctionDeclaration if Pkgbuild._FUNCTION_DECLARATION.match(token):
                key = f"{token}{PkgbuildToken.FunctionDeclaration}"
                value = Pkgbuild._parse_function(parser)
                return token, PkgbuildPatch(key, value)  # this is not mistake, assign to token without ()

            # some random token received without continuation, lets guess it is empty assignment (i.e. key=)
            case other if other is not None:
                return Pkgbuild._parse_token(other, parser)

            # reached the end of the parser
            case None:
                raise StopIteration

    def get_as(self, key: str, return_type: type[T], **kwargs: T | U) -> T | U:
        """
        type guard for getting value by key

        Args:
            key(str): key name
            return_type(type[T]): return type, either ``str`` or ``list[str]``
            default(U, optional): default value to return if no key found

        Returns:
            T | U: value associated with key or default value if no value found and fallback is provided

        Raises:
            KeyError: if no key found and no default has been provided
        """
        del return_type

        if key not in self:
            if "default" in kwargs:
                return kwargs["default"]
            raise KeyError(key)

        return cast(T, self[key])

    def packages(self) -> dict[str, Self]:
        """
        extract properties from internal package functions

        Returns:
            dict[str, Self]: map of package name to its inner properties if defined
        """
        packages = [self["pkgname"]] if isinstance(self["pkgname"], str) else self["pkgname"]

        def io(package_name: str) -> IO[str]:
            # try to read package specific function and fallback to default otherwise
            content = self.get_as(f"package_{package_name}", str, default=None) or self.get_as("package", str)
            return StringIO(content)

        return {package: self.from_io(io(package)) for package in packages}

    def __getitem__(self, key: str) -> str | list[str]:
        """
        get the field of the PKGBUILD

        Args:
            key(str): key name

        Returns:
            str | list[str]: value by the key
        """
        return self.fields[key].substitute(self.variables)

    def __iter__(self) -> Iterator[str]:
        """
        iterate over the fields

        Returns:
            Iterator[str]: keys iterator
        """
        return iter(self.fields)

    def __len__(self) -> int:
        """
        get length of the mapping

        Returns:
            int: amount of the fields in this PKGBUILD
        """
        return len(self.fields)
