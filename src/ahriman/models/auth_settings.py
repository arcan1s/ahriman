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
from __future__ import annotations

from enum import StrEnum


class AuthSettings(StrEnum):
    """
    web authorization type

    Attributes:
        Disabled(AuthSettings): (class attribute) authorization is disabled
        Configuration(AuthSettings): (class attribute) configuration based authorization
        OAuth(AuthSettings): (class attribute) OAuth based provider
        PAM(AuthSettings): (class attribute) PAM based provider
    """

    Disabled = "disabled"
    Configuration = "configuration"
    OAuth = "oauth2"
    PAM = "pam"

    @property
    def is_enabled(self) -> bool:
        """
        get enabled flag

        Returns:
            bool: ``False`` in case if authorization is disabled and ``True`` otherwise
        """
        return self != AuthSettings.Disabled

    @staticmethod
    def from_option(value: str) -> AuthSettings:
        """
        construct value from configuration

        Args:
            value(str): configuration value

        Returns:
            AuthSettings: parsed value
        """
        match value.lower():
            case "configuration" | "mapping":
                return AuthSettings.Configuration
            case "oauth" | "oauth2":
                return AuthSettings.OAuth
            case "pam":
                return AuthSettings.PAM
            case _:
                return AuthSettings.Disabled
