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
import re

from dataclasses import dataclass
from functools import cached_property
from pathlib import Path


@dataclass(frozen=True)
class ScanPaths:
    """
    paths used for scan filesystem

    Attributes:
        paths(list[str]): list of regular expressions to be used to match paths
    """

    paths: list[str]

    @cached_property
    def patterns(self) -> list[re.Pattern[str]]:
        """
        compiled regular expressions

        Returns:
            list[re.Pattern]: a list of compiled regular expressions
        """
        return [re.compile(path) for path in self.paths]

    def is_allowed(self, path: Path) -> bool:
        """
        check whether path is allowed to scan or not

        Args:
            path(Path): path to be checked

        Returns:
            bool: ``True`` in case if :attr:`paths` contains at least one element to which the path is matched
            and ``False`` otherwise
        """
        return any(pattern.match(str(path)) for pattern in self.patterns)
