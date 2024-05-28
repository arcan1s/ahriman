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
from pathlib import Path


@dataclass(frozen=True, kw_only=True)
class FilesystemPackage:
    """
    class representing a simplified model for the package installed to filesystem

    Attributes:
        package_name(str): package name
        dependencies(list[str]): list of package dependencies
        directories(list[Path]): list of directories this package contains
        files(list[Path]): list of files this package contains
        groups(list[str]): list of groups of the package
    """

    package_name: str
    groups: set[str]
    dependencies: set[str]
    directories: list[Path] = field(default_factory=list)
    files: list[Path] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """
        quick check if this package must be used for the dependencies calculation. It checks that
        1) package is not in the base group

        Returns:
            bool: True in case if this package must be used for the dependencies calculation or False otherwise
        """
        return "base" not in self.groups

    def __repr__(self):
        return f'FilesystemPackage(package_name="{self.package_name}", dependencies={self.dependencies})'
