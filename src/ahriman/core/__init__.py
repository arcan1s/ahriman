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
from collections.abc import Iterator
from contextvars import ContextVar
from typing import Any, TypeVar

from ahriman.models.context_key import ContextKey


T = TypeVar("T")


class _Context:
    """
    simple ahriman global context implementation
    """

    def __init__(self) -> None:
        """"""
        self._content: dict[str, Any] = {}

    def get(self, key: ContextKey[T] | type[T]) -> T:
        """
        get value for the specified key

        Args:
            key(ContextKey[T] | type[T]): context key name

        Returns:
            T: value associated with the key

        Raises:
            KeyError: in case if the specified context variable was not found
            ValueError: in case if type of value is not an instance of specified return type
        """
        if not isinstance(key, ContextKey):
            key = ContextKey.from_type(key)

        if key.key not in self._content:
            raise KeyError(key.key)
        value = self._content[key.key]
        if not isinstance(value, key.return_type):
            raise ValueError(f"Value {value} is not an instance of {key.return_type}")

        return value

    def set(self, key: ContextKey[T] | type[T], value: T) -> None:
        """
        set value for the specified key

        Args:
            key(ContextKey[T] | type[T]): context key name
            value(T): context value associated with the specified key

        Raises:
            KeyError: in case if the specified context variable already exists
            ValueError: in case if type of value is not an instance of specified return type
        """
        if not isinstance(key, ContextKey):
            key = ContextKey.from_type(key)

        if key.key in self._content:
            raise KeyError(key.key)
        if not isinstance(value, key.return_type):
            raise ValueError(f"Value {value} is not an instance of {key.return_type}")

        self._content[key.key] = value

    def __iter__(self) -> Iterator[str]:
        """
        iterate over keys in local storage

        Returns:
            str: context key iterator
        """
        return iter(self._content)

    def __len__(self) -> int:
        """
        get count of the context variables set

        Returns:
            int: count of stored context variables
        """
        return len(self._content)


context = ContextVar("context", default=_Context())
