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

from enum import Enum, auto
from typing import Type


class SmtpSSLSettings(Enum):
    """
    SMTP SSL mode enumeration
    :cvar Disabled: no SSL enabled
    :cvar SSL: use SMTP_SSL instead of normal SMTP client
    :cvar STARTTLS: use STARTTLS in normal SMTP client
    """

    Disabled = auto()
    SSL = auto()
    STARTTLS = auto()

    @classmethod
    def from_option(cls: Type[SmtpSSLSettings], value: str) -> SmtpSSLSettings:
        """
        construct value from configuration
        :param value: configuration value
        :return: parsed value
        """
        if value.lower() in ("ssl", "ssl/tls"):
            return cls.SSL
        if value.lower() in ("starttls",):
            return cls.STARTTLS
        return cls.Disabled
