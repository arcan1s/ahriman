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
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from ahriman.core.repository.executor import Executor
from ahriman.core.repository.update_handler import UpdateHandler
from ahriman.core.util import package_like
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource


class Repository(Executor, UpdateHandler):
    """
    base repository control class
    """

    def load_archives(self, packages: Iterable[Path]) -> List[Package]:
        """
        load packages from list of archives

        Args:
            packages(Iterable[Path]): paths to package archives

        Returns:
            List[Package]: list of read packages
        """
        result: Dict[str, Package] = {}
        # we are iterating over bases, not single packages
        for full_path in packages:
            try:
                local = Package.load(str(full_path), PackageSource.Archive, self.pacman, self.aur_url)
                current = result.setdefault(local.base, local)
                if current.version != local.version:
                    # force version to max of them
                    self.logger.warning("version of %s differs, found %s and %s",
                                        current.base, current.version, local.version)
                    if current.is_outdated(local, self.paths, calculate_version=False):
                        current.version = local.version
                current.packages.update(local.packages)
            except Exception:
                self.logger.exception("could not load package from %s", full_path)
        return list(result.values())

    def packages(self) -> List[Package]:
        """
        generate list of repository packages

        Returns:
            List[Package]: list of packages properties
        """
        return self.load_archives(filter(package_like, self.paths.repository.iterdir()))

    def packages_built(self) -> List[Path]:
        """
        get list of files in built packages directory

        Returns:
            List[Path]: list of filenames from the directory
        """
        return list(filter(package_like, self.paths.packages.iterdir()))

    def packages_depends_on(self, depends_on: Optional[Iterable[str]]) -> List[Package]:
        """
        extract list of packages which depends on specified package

        Args:
            depends_on(Optional[Iterable[str]]): dependencies of the packages

        Returns:
            List[Package]: list of repository packages which depend on specified packages
        """
        packages = self.packages()
        if depends_on is None:
            return packages  # no list provided extract everything by default
        depends_on = set(depends_on)

        return [
            package
            for package in packages
            if depends_on is None or depends_on.intersection(package.full_depends(self.pacman, packages))
        ]
