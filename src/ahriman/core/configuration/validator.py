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
from cerberus import TypeDefinition, Validator as RootValidator  # type: ignore
from pathlib import Path
from typing import Any, List

from ahriman.core.configuration import Configuration


class Validator(RootValidator):  # type: ignore
    """
    class which defines custom validation methods for the service configuration

    Attributes:
        instance(Configuration): configuration instance
    """

    types_mapping = RootValidator.types_mapping.copy()
    types_mapping["path"] = TypeDefinition("path", (Path,), ())

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        default constructor

        Args:
            instance(Configuration): configuration instance used for extraction
            *args(Any): positional arguments to be passed to base validator
            **kwargs(): keyword arguments to be passed to base validator
        """
        RootValidator.__init__(self, *args, **kwargs)
        self.instance: Configuration = kwargs["instance"]

    def _normalize_coerce_absolute_path(self, value: str) -> Path:
        """
        extract path from string value

        Args:
            value(str): converting value

        Returns:
            Path: value converted to path instance according to configuration rules
        """
        converted: Path = self.instance.converters["path"](value)
        return converted

    def _normalize_coerce_boolean(self, value: str) -> bool:
        """
        extract boolean from string value

        Args:
            value(str): converting value

        Returns:
            bool: value converted to boolean according to configuration rules
        """
        # pylint: disable=protected-access
        converted: bool = self.instance._convert_to_boolean(value)  # type: ignore
        return converted

    def _normalize_coerce_integer(self, value: str) -> int:
        """
        extract integer from string value

        Args:
            value(str): converting value

        Returns:
            int: value converted to int according to configuration rules
        """
        return int(value)

    def _normalize_coerce_list(self, value: str) -> List[str]:
        """
        extract string list from string value

        Args:
            value(str): converting value

        Returns:
            List[str]: value converted to string list instance according to configuration rules
        """
        converted: List[str] = self.instance.converters["list"](value)
        return converted

    def _validate_path_exists(self, constraint: bool, field: str, value: Path) -> None:
        """
        check if paths exists

        Args:
            constraint(bool): True in case if path must exist and False otherwise
            field(str): field name to be checked
            value(Path): value to be checked

        Examples:
            The rule's arguments are validated against this schema:
            {"type": "boolean"}
        """
        if constraint and not value.exists():
            self._error(field, f"Path {value} must exist")
