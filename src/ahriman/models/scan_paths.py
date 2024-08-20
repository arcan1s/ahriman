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
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, kw_only=True)
class ScanPaths:
    """
    paths used for scan filesystem

    Attributes:
        allowed_paths(list[Path]): list of whitelisted paths
        blacklisted_paths(list[Path]): list of paths to be skipped from scan
    """

    allowed_paths: list[Path]
    blacklisted_paths: list[Path]

    def __post_init__(self) -> None:
        """
        compute relative to / paths
        """
        object.__setattr__(self, "allowed_paths", [path.relative_to("/") for path in self.allowed_paths])
        object.__setattr__(self, "blacklisted_paths", [path.relative_to("/") for path in self.blacklisted_paths])

    def is_allowed(self, path: Path) -> bool:
        """
        check whether path is allowed to scan or not

        Args:
            path(Path): path to be checked

        Returns:
            bool: ``True`` in case if :attr:`allowed_paths` contains element which is parent for the path and
            :attr:`blacklisted_paths` doesn't and ``False`` otherwise
        """
        if any(path.is_relative_to(blacklisted) for blacklisted in self.blacklisted_paths):
            return False  # path is blacklisted
        # check if we actually have to check this path
        return any(path.is_relative_to(allowed) for allowed in self.allowed_paths)
