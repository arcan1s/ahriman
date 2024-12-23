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
from typing import Any

from ahriman.core.exceptions import OptionError


class ConfigurationMultiDict(dict[str, Any]):
    """
    wrapper around :class:`dict` to handle multiple configuration keys as lists if they end with ``[]``.

    Examples:
        This class is designed to be used only with :class:`configparser.RawConfigParser` class, but idea is that
        if the key ends with ``[]`` it will be treated as array and the result will be appended to the current value.
        In addition, if the value is empty, then it will clear previous values, e.g.:

            >>> data = ConfigurationMultiDict()
            >>>
            >>> data["single"] = "value"  # append normal key
            >>> print(data)  # {"single": "value"}
            >>>
            >>> data["array[]"] = ["value1"]  # append array value
            >>> data["array[]"] = ["value2"]
            >>> print(data)  # {"single": "value", "array": ["value1 value2"]}
            >>>
            >>> data["array[]"] = [""]  # clear previous values
            >>> data["array[]"] = ["value3"]
            >>> print(data)  # {"single": "value", "array": ["value3"]}
    """

    def _set_array_value(self, key: str, value: Any) -> None:
        """
        set array value. If the key already exists in the dictionary, its value will be prepended to new value

        Args:
            key(str): key to insert
            value(Any): value of the related key

        Raises:
            OptionError: if the key already exists in the dictionary, but not a single value list or a string
        """
        match self.get(key):
            case [current_value] | str(current_value):  # type: ignore[misc]
                value = f"{current_value} {value}"
            case None:
                pass
            case other:
                raise OptionError(other)
        super().__setitem__(key, [value])

    def __setitem__(self, key: str, value: Any) -> None:
        """
        set ``key`` to ``value``. If the value equals to ``[""]`` (array with empty string), then the key
        will be removed (as expected from :class:`configparser.RawConfigParser`). If the key ends with
        ``[]``, the value will be treated as an array and vice versa.

        Args:
            key(str): key to insert
            value(Any): value of the related key

        Raises:
            OptionError: if ``key`` contains ``[]``, but not at the end of the string (e.g. ``prefix[]suffix``)
        """
        real_key, is_key_array, remaining = key.partition("[]")
        if remaining:
            raise OptionError(key)

        match value:
            case [""]:  # empty value key
                self.pop(real_key, None)
            case [array_value] if is_key_array:  # update array value
                self._set_array_value(real_key, array_value)
            case _:  # normal key
                super().__setitem__(real_key, value)
