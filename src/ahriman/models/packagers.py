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
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Packagers:
    """
    holder for packagers overrides

    Attributes:
        default(str | None): default packager username if any to be used if no override for the specified base was found
        overrides: dict[str, str | None]: packager username override for specific package base
    """

    default: str | None = None
    overrides: dict[str, str | None] = field(default_factory=dict)

    def for_base(self, package_base: str) -> str | None:
        """
        extract username for the specified package base

        Args:
            package_base(str): package base to lookup

        Returns:
            str | None: package base override if set and default packager username otherwise
        """
        return self.overrides.get(package_base) or self.default
