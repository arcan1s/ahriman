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
from __future__ import annotations

from enum import StrEnum


class ReportSettings(StrEnum):
    """
    report targets enumeration

    Attributes:
        Disabled(ReportSettings): (class attribute) option which generates no report for testing purpose
        HTML(ReportSettings): (class attribute) html report generation
        Email(ReportSettings): (class attribute) email report generation
        Console(ReportSettings): (class attribute) print result to console
        Telegram(ReportSettings): (class attribute) markdown report to telegram channel
        RemoteCall(ReportSettings): (class attribute) remote ahriman server call
    """

    Disabled = "disabled"  # for testing purpose
    HTML = "html"
    Email = "email"
    Console = "console"
    Telegram = "telegram"
    RemoteCall = "remote-call"

    @staticmethod
    def from_option(value: str) -> ReportSettings:
        """
        construct value from configuration

        Args:
            value(str): configuration value

        Returns:
            ReportSettings: parsed value
        """
        match value.lower():
            case "html":
                return ReportSettings.HTML
            case "email":
                return ReportSettings.Email
            case "console":
                return ReportSettings.Console
            case "telegram":
                return ReportSettings.Telegram
            case "ahriman" | "remote-call":
                return ReportSettings.RemoteCall
            case _:
                return ReportSettings.Disabled
