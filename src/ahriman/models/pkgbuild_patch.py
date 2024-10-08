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
import shlex

from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Generator, Self

from ahriman.core.configuration.shell_template import ShellTemplate
from ahriman.core.utils import dataclass_view, filter_json


@dataclass(frozen=True)
class PkgbuildPatch:
    """
    wrapper for patching PKBGUILDs

    Attributes:
        key(str | None): name of the property in PKGBUILD, e.g. version, url etc. If not set, patch will be
            considered as full PKGBUILD diffs
        value(str | list[str]): value of the stored PKGBUILD property. It must be either string or list of string
            values
    """

    key: str | None
    value: str | list[str]

    quote = shlex.quote

    def __post_init__(self) -> None:
        """
        remove empty key
        """
        object.__setattr__(self, "key", self.key or None)

    @property
    def is_function(self) -> bool:
        """
        parse key and define whether it function or not

        Returns:
            bool: ``True`` in case if key ends with parentheses and ``False`` otherwise
        """
        return self.key is not None and self.key.endswith("()")

    @property
    def is_plain_diff(self) -> bool:
        """
        check if patch is full diff one or just single-variable patch

        Returns:
            bool: ``True`` in case key set and ``False`` otherwise
        """
        return self.key is None

    @classmethod
    def from_env(cls, variable: str) -> Self:
        """
        construct patch from environment variable. Functions are not supported

        Args:
            variable(str): variable in bash form, i.e. KEY=VALUE

        Returns:
            Self: package properties
        """
        key, *value_parts = variable.split("=", maxsplit=1)
        raw_value = next(iter(value_parts), "")  # extract raw value
        return cls(key, cls.parse(raw_value))

    @classmethod
    def from_json(cls, dump: dict[str, Any]) -> Self:
        """
        construct patch descriptor from the json dump

        Args:
            dump(dict[str, Any]): json dump body

        Returns:
            Self: patch object
        """
        # filter to only known fields
        known_fields = [pair.name for pair in fields(cls)]
        return cls(**filter_json(dump, known_fields))

    @staticmethod
    def parse(source: str) -> str | list[str]:
        """
        parse string value to the PKGBUILD patch value. This method simply takes string, tries to identify it as array
        or just string and return the respective value. Functions should be processed correctly, however, not guaranteed

        Args:
            source(str): source string to parse

        Returns:
            str | list[str]: parsed value either string or list of strings
        """
        if source.startswith("(") and source.endswith(")"):
            return shlex.split(source[1:-1])  # arrays for poor
        return PkgbuildPatch.unquote(source)

    @staticmethod
    def unquote(source: str) -> str:
        """
        like :func:`shlex.quote()`, but opposite

        Args:
            source(str): source string to remove quotes

        Returns:
            str: string with quotes removed

        Raises:
            ValueError: if no closing quotation
        """

        def generator() -> Generator[str, None, None]:
            token = None
            for char in source:
                if token is not None:
                    if char == token:
                        token = None  # closed quote
                    else:
                        yield char  # character inside quotes
                elif char in ("'", "\""):
                    token = char  # first quote found
                else:
                    yield char  # normal character

            if token is not None:
                raise ValueError("No closing quotation")

        return "".join(generator())

    def serialize(self) -> str:
        """
        serialize key-value pair into PKGBUILD string. List values will be put inside parentheses. All string
        values (including the ones inside list values) will be put inside quotes, no shell variables expanding supported
        at the moment

        Returns:
            str: serialized key-value pair, print-friendly
        """
        if isinstance(self.value, list):  # list like
            value = " ".join(map(PkgbuildPatch.quote, self.value))
            return f"""{self.key}=({value})"""
        if self.is_plain_diff:  # no additional logic for plain diffs
            return self.value
        # we suppose that function values are only supported in string-like values
        if self.is_function:
            return f"{self.key} {self.value}"  # no quoting enabled here
        return f"""{self.key}={PkgbuildPatch.quote(self.value)}"""

    def substitute(self, variables: dict[str, str]) -> str | list[str]:
        """
        substitute variables into the value

        Args:
            variables(dict[str, str]): map of variables available for usage

        Returns:
            str | list[str]: substituted value. All unknown variables will remain as links to their values.
            This function doesn't support recursive substitution
        """
        if isinstance(self.value, str):
            return ShellTemplate(self.value).shell_substitute(variables)
        return [ShellTemplate(value).shell_substitute(variables) for value in self.value]

    def view(self) -> dict[str, Any]:
        """
        generate json patch view

        Returns:
            dict[str, Any]: json-friendly dictionary
        """
        return dataclass_view(self)

    def write(self, pkgbuild_path: Path) -> None:
        """
        write serialized value into PKGBUILD by specified path

        Args:
            pkgbuild_path(Path): path to PKGBUILD file
        """
        with pkgbuild_path.open("a", encoding="utf8") as pkgbuild:
            pkgbuild.write("\n")  # in case if file ends without new line we are appending it at the end
            pkgbuild.write(self.serialize())
            pkgbuild.write("\n")  # append new line after the values
