#
# Copyright (c) 2021 ahriman team.
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

from enum import Enum
from typing import Type

from ahriman.core.exceptions import InvalidOption


class AuthSettings(Enum):
    """
    web authorization type
    :cvar Disabled: authorization is disabled
    :cvar Configuration: configuration based authorization
    :cvar OAuth: OAuth based provider
    """

    Disabled = "disabled"
    Configuration = "configuration"
    OAuth = "oauth2"

    @classmethod
    def from_option(cls: Type[AuthSettings], value: str) -> AuthSettings:
        """
        construct value from configuration
        :param value: configuration value
        :return: parsed value
        """
        if value.lower() in ("disabled", "no"):
            return cls.Disabled
        if value.lower() in ("configuration", "mapping"):
            return cls.Configuration
        if value.lower() in ('oauth', 'oauth2'):
            return cls.OAuth
        raise InvalidOption(value)

    @property
    def is_enabled(self) -> bool:
        """
        :return: False in case if authorization is disabled and True otherwise
        """
        if self == AuthSettings.Disabled:
            return False
        return True
