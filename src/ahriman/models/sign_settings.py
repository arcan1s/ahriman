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
from __future__ import annotations

from enum import StrEnum


class SignSettings(StrEnum):
    """
    sign targets enumeration

    Attributes:
        Disabled(SignSettings): option which generates no report for testing purpose
        Packages(SignSettings): sign each package
        Repository(SignSettings): sign repository database file
    """

    Disabled = "disabled"
    Packages = "packages"
    Repository = "repository"

    @staticmethod
    def from_option(value: str) -> SignSettings:
        """
        construct value from configuration

        Args:
            value(str): configuration value

        Returns:
            SignSettings: parsed value
        """
        match value.lower():
            case "package" | "packages" | "sign-package":
                return SignSettings.Packages
            case "repository" | "sign-repository":
                return SignSettings.Repository
            case _:
                return SignSettings.Disabled
