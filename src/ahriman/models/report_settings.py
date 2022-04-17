#
# Copyright (c) 2021-2022 ahriman team.
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


class ReportSettings(Enum):
    """
    report targets enumeration

    Attributes:
      Disabled(ReportSettings): (class attribute) option which generates no report for testing purpose
      HTML(ReportSettings): (class attribute) html report generation
      Email(ReportSettings): (class attribute) email report generation
      Console(ReportSettings): (class attribute) print result to console
      Telegram(ReportSettings): (class attribute) markdown report to telegram channel
    """

    Disabled = "disabled"  # for testing purpose
    HTML = "html"
    Email = "email"
    Console = "console"
    Telegram = "telegram"

    @classmethod
    def from_option(cls: Type[ReportSettings], value: str) -> ReportSettings:
        """
        construct value from configuration

        Args:
          value(str): configuration value

        Returns:
          ReportSettings: parsed value
        """
        if value.lower() in ("html",):
            return cls.HTML
        if value.lower() in ("email",):
            return cls.Email
        if value.lower() in ("console",):
            return cls.Console
        if value.lower() in ("telegram",):
            return cls.Telegram
        return cls.Disabled
