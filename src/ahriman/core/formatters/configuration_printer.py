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
from typing import ClassVar

from ahriman.core.formatters.string_printer import StringPrinter
from ahriman.models.property import Property


class ConfigurationPrinter(StringPrinter):
    """
    print content of the configuration section

    Attributes:
        HIDE_KEYS(list[str]): (class attribute) hide values for mentioned keys. This list must be used in order to hide
            passwords from outputs
        values(dict[str, str]): configuration values dictionary
    """

    HIDE_KEYS: ClassVar[list[str]] = [
        "api_key",  # telegram key
        "client_secret",  # oauth secret
        "cookie_secret_key",  # cookie secret key
        "password",  # generic password (github, email, web server, etc)
        "salt",  # password default salt
        "secret_key",  # aws secret key
    ]

    def __init__(self, section: str, values: dict[str, str]) -> None:
        """
        Args:
            section(str): section name
            values(dict[str, str]): configuration values dictionary
        """
        StringPrinter.__init__(self, f"[{section}]")
        self.values = values

    def properties(self) -> list[Property]:
        """
        convert content into printable data

        Returns:
            list[Property]: list of content properties
        """
        return [
            Property(key, value, is_required=key not in self.HIDE_KEYS)
            for key, value in sorted(self.values.items())
        ]
