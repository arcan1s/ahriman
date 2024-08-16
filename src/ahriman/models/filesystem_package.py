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
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from ahriman.core.utils import trim_package


@dataclass(frozen=True, kw_only=True)
class FilesystemPackage:
    """
    class representing a simplified model for the package installed to filesystem

    Attributes:
        package_name(str): package name
        depends(set[str]): list of package dependencies
        directories(set[Path]): list of directories this package contains
        files(list[Path]): list of files this package contains
        opt_depends(set[str]): list of package optional dependencies
    """

    package_name: str
    depends: set[str]
    opt_depends: set[str]
    directories: list[Path] = field(default_factory=list)
    files: list[Path] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        update dependencies list accordingly
        """
        object.__setattr__(self, "depends", {trim_package(package) for package in self.depends})
        object.__setattr__(self, "opt_depends", {trim_package(package) for package in self.opt_depends})

    def depends_on(self, package_name: str, *, include_optional: bool) -> bool:
        """
        check if package depends on given package name

        Args:
            package_name(str): package name to check dependencies
            include_optional(bool): include optional dependencies to check

        Returns:
            bool: ``True`` in case if the given package in the dependencies lists
        """
        if package_name in self.depends:
            return True
        if include_optional and package_name in self.opt_depends:
            return True
        return False

    def is_root_package(self, packages: Iterable[FilesystemPackage], *, include_optional: bool) -> bool:
        """
        check if the package is the one of the root packages. This method checks if there are any packages which are
        dependency of the package and - to avoid circular dependencies - does not depend on the package. In addition,
        if ``include_optional`` is set to ``True``, then it will also check optional dependencies of the package

        Args:
            packages(Iterable[FilesystemPackage]): list of packages in which we need to search
            include_optional(bool): include optional dependencies to check

        Returns:
            bool: whether this package depends on any other package in the list of packages
        """
        return not any(
            package
            for package in packages
            if self.depends_on(package.package_name, include_optional=include_optional)
            and not package.depends_on(self.package_name, include_optional=False)
        )
