#
# Copyright (c) 2021-2023 ahriman team.
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

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class PkgbuildPatch:
    """
    wrapper for patching PKBGUILDs

    Attributes:
        key(str | None): name of the property in PKGBUILD, e.g. version, url etc. If not set, patch will be
            considered as full PKGBUILD diffs
        value(str | list[str]): value of the stored PKGBUILD property. It must be either string or list of string
            values
        unsafe(bool): if set, value will be not quoted, might break PKGBUILD
    """

    key: str | None
    value: str | list[str]
    unsafe: bool = field(default=False, kw_only=True)

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
            bool: True in case if key ends with parentheses and False otherwise
        """
        return self.key is not None and self.key.endswith("()")

    @property
    def is_plain_diff(self) -> bool:
        """
        check if patch is full diff one or just single-variable patch

        Returns:
            bool: True in case key set and False otherwise
        """
        return self.key is None

    def quote(self, value: str) -> str:
        """
        quote value according to the unsafe flag

        Args:
            value(str): value to be quoted

        Returns:
            str: quoted string in case if unsafe is False and as is otherwise
        """
        return value if self.unsafe else shlex.quote(value)

    def serialize(self) -> str:
        """
        serialize key-value pair into PKGBUILD string. List values will be put inside parentheses. All string
        values (including the ones inside list values) will be put inside quotes, no shell variables expanding supported
        at the moment

        Returns:
            str: serialized key-value pair, print-friendly
        """
        if isinstance(self.value, list):  # list like
            value = " ".join(map(self.quote, self.value))
            return f"""{self.key}=({value})"""
        if self.is_plain_diff:  # no additional logic for plain diffs
            return self.value
        # we suppose that function values are only supported in string-like values
        if self.is_function:
            return f"{self.key} {self.value}"  # no quoting enabled here
        return f"""{self.key}={self.quote(self.value)}"""

    def write(self, pkgbuild_path: Path) -> None:
        """
        write serialized value into PKGBUILD by specified path

        Args:
            pkgbuild_path(Path): path to PKGBUILD file
        """
        with pkgbuild_path.open("a") as pkgbuild:
            pkgbuild.write("\n")  # in case if file ends without new line we are appending it at the end
            pkgbuild.write(self.serialize())
            pkgbuild.write("\n")  # append new line after the values
