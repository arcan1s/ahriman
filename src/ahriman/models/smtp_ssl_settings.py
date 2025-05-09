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
from __future__ import annotations

from enum import StrEnum


class SmtpSSLSettings(StrEnum):
    """
    SMTP SSL mode enumeration

    Attributes:
        Disabled(SmtpSSLSettings): no SSL enabled
        SSL(SmtpSSLSettings): use SMTP_SSL instead of normal SMTP client
        STARTTLS(SmtpSSLSettings): use STARTTLS in normal SMTP client
    """

    Disabled = "disabled"
    SSL = "ssl"
    STARTTLS = "starttls"

    @staticmethod
    def from_option(value: str) -> SmtpSSLSettings:
        """
        construct value from configuration

        Args:
            value(str): configuration value

        Returns:
            SmtpSSLSettings: parsed value
        """
        match value.lower():
            case "ssl" | "ssl/tls":
                return SmtpSSLSettings.SSL
            case "starttls":
                return SmtpSSLSettings.STARTTLS
            case _:
                return SmtpSSLSettings.Disabled
