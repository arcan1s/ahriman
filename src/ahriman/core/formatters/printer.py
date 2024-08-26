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
import builtins

from collections.abc import Callable

from ahriman.models.property import Property


class Printer:
    """
    base class for formatters
    """

    _print = builtins.print  # do not shadow with method

    def print(self, *, verbose: bool, log_fn: Callable[[str], None] = _print, separator: str = ": ") -> None:
        """
        print content

        Args:
            verbose(bool): print all fields
            log_fn(Callable[[str], None], optional): logger function to log data (Default value = print)
            separator(str, optional): separator for property name and property value (Default value = ": ")
        """
        if (title := self.title()) is not None:
            log_fn(title)
        for prop in self.properties():
            if not verbose and not prop.is_required:
                continue
            indent = "\t" * prop.indent
            log_fn(f"{indent}{prop.name}{separator}{prop.value}")

    def properties(self) -> list[Property]:
        """
        convert content into printable data

        Returns:
            list[Property]: list of content properties
        """
        return []

    # pylint: disable=redundant-returns-doc
    def title(self) -> str | None:
        """
        generate entry title from content

        Returns:
            str | None: content title if it can be generated and ``None`` otherwise
        """
        return None

    def __call__(self, *, verbose: bool, log_fn: Callable[[str], None] = _print, separator: str = ": ") -> None:
        """
        print content. Shortcut for :func:`print()`

        Args:
            verbose(bool): print all fields
            log_fn(Callable[[str], None], optional): logger function to log data (Default value = print)
            separator(str, optional): separator for property name and property value (Default value = ": ")
        """
        self.print(verbose=verbose, log_fn=log_fn, separator=separator)
