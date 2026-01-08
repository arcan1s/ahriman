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
import ipaddress

from cerberus import TypeDefinition, Validator as RootValidator  # type: ignore[import-untyped]
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ahriman.core.configuration import Configuration


class Validator(RootValidator):
    """
    class which defines custom validation methods for the service configuration

    Attributes:
        configuration(Configuration): configuration instance
    """

    types_mapping = RootValidator.types_mapping | {
        "path": TypeDefinition("path", (Path,), ()),
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Args:
            configuration(Configuration): configuration instance used for extraction
            *args(Any): positional arguments to be passed to base validator
            **kwargs(Any): keyword arguments to be passed to base validator
        """
        RootValidator.__init__(self, *args, **kwargs)
        self.configuration: Configuration = kwargs["configuration"]

    def _normalize_coerce_absolute_path(self, value: str) -> Path:
        """
        extract path from string value

        Args:
            value(str): converting value

        Returns:
            Path: value converted to path instance according to configuration rules
        """
        converted: Path = self.configuration.converters["path"](value)
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
        converted: bool = self.configuration._convert_to_boolean(value)  # type: ignore[attr-defined]
        return converted

    def _normalize_coerce_integer(self, value: str) -> int:
        """
        extract integer from string value

        Args:
            value(str): converting value

        Returns:
            int: value converted to int according to configuration rules
        """
        del self
        return int(value)

    def _normalize_coerce_list(self, value: str) -> list[str]:
        """
        extract string list from string value

        Args:
            value(str): converting value

        Returns:
            list[str]: value converted to string list instance according to configuration rules
        """
        converted: list[str] = self.configuration.converters["list"](value)
        return converted

    def _validate_is_ip_address(self, constraint: list[str], field: str, value: str) -> None:
        """
        check if the specified value is valid ip address

        Args:
            constraint(list[str]): optional list of allowed special words (e.g. ``localhost``)
            field(str): field name to be checked
            value(Path): value to be checked

        Examples:
            The rule's arguments are validated against this schema:
            {"type": "list", "schema": {"type": "string"}}
        """
        if value in constraint:
            return
        try:
            ipaddress.ip_address(value)
        except ValueError:
            self._error(field, f"Value {value} must be valid IP address")

    def _validate_is_url(self, constraint: list[str], field: str, value: str) -> None:
        """
        check if the specified value is a valid url

        Args:
            constraint(list[str]): optional list of supported schemas. If empty, no schema validation will be performed
            field(str): field name to be checked
            value(str): value to be checked

        Examples:
            The rule's arguments are validated against this schema:
            {"type": "list", "schema": {"type": "string"}}
        """
        match urlparse(value):  # it probably will never rise exceptions on parse
            case url if not url.scheme:
                self._error(field, f"Url scheme is not set for {value}")
            case url if not url.netloc and url.scheme not in ("file",):
                self._error(field, f"Location must be set for url {value} of scheme {url.scheme}")
            case url if constraint and url.scheme not in constraint:
                self._error(field, f"Url {value} scheme must be one of {constraint}")

    def _validate_path_exists(self, constraint: bool, field: str, value: Path) -> None:
        """
        check if paths exists

        Args:
            constraint(bool): ``True`` in case if path must exist and ``False`` otherwise
            field(str): field name to be checked
            value(Path): value to be checked

        Examples:
            The rule's arguments are validated against this schema:
            {"type": "boolean"}
        """
        match value.exists():
            case True if not constraint:
                self._error(field, f"Path {value} must not exist")
            case False if constraint:
                self._error(field, f"Path {value} must exist")

    def _validate_path_type(self, constraint: str, field: str, value: Path) -> None:
        """
        check if paths is file, directory or whatever. The match will be performed as call of ``is_{constraint}``
        method of the path object

        Args:
            constraint(str): path type to be matched
            field(str): field name to be checked
            value(Path): value to be checked

        Examples:
            The rule's arguments are validated against this schema:
            {"type": "string"}
        """
        fn = getattr(value, f"is_{constraint}")
        if not fn():
            self._error(field, f"Path {value} must be type of {constraint}")
