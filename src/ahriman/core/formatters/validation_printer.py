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
from collections.abc import Generator
from typing import Any

from ahriman.core.formatters.string_printer import StringPrinter
from ahriman.models.property import Property


class ValidationPrinter(StringPrinter):
    """
    print content of the validation errors

    Attributes:
        node(str): root level name
        errors(list[str | dict[str, Any]]): validation errors
    """

    def __init__(self, node: str, errors: list[str | dict[str, Any]]) -> None:
        """
        Args:
            node(str): root level name
            errors(list[str | dict[str, Any]]): validation errors
        """
        StringPrinter.__init__(self, node)
        self.node = node
        self.errors = errors

    @staticmethod
    def get_error_messages(node: str, errors: list[str | dict[str, Any]],
                           current_level: int = 1) -> Generator[Property, None, None]:
        """
        extract default error message from cerberus class

        Args:
            node(str): current node level name
            errors(list[str | dict[str, Any]]): current node validation errors
            current_level(int, optional): current level number (Default value = 1)

        Yields:
            Property: error messages from error tree
        """
        for error in errors:
            if not isinstance(error, str):  # child nodes errors
                for child_node, child_errors in error.items():
                    # increase indentation instead of nodes concatenations
                    # sometimes it is not only nodes, but rules themselves
                    yield from ValidationPrinter.get_error_messages(child_node, child_errors, current_level + 1)
            else:  # current node errors
                yield Property(node, error, is_required=True, indent=current_level)

    def properties(self) -> list[Property]:
        """
        convert content into printable data

        Returns:
            list[Property]: list of content properties
        """
        return list(self.get_error_messages(self.node, self.errors))
