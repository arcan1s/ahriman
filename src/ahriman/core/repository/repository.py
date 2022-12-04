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


class Repository(Executor, UpdateHandler):
    """
    base repository control class

    Examples:
        This class along with traits provides access to local repository actions, e.g. remove packages, update packages,
        sync local repository to remote, generate report, etc::

            >>> from ahriman.core.configuration import Configuration
            >>> from ahriman.core.database import SQLite
            >>>
            >>> configuration = Configuration()
            >>> database = SQLite.load(configuration)
            >>> repository = Repository("x86_64", configuration, database, report=True, unsafe=False)
            >>> known_packages = repository.packages()
            >>>
            >>> build_result = repository.process_build(known_packages)
            >>> built_packages = repository.packages_built()
            >>> update_result = repository.process_update(built_packages)
            >>>
            >>> repository.triggers.on_result(update_result, repository.packages())
    """

    def load_archives(self, packages: Iterable[Path]) -> List[Package]:
        """
        load packages from list of archives

        Args:
            packages(Iterable[Path]): paths to package archives

        Returns:
            List[Package]: list of read packages
        """
        sources = self.database.remotes_get()

        result: Dict[str, Package] = {}
        # we are iterating over bases, not single packages
        for full_path in packages:
            try:
                local = Package.from_archive(full_path, self.pacman, None)
                local.remote = sources.get(local.base)

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

    def packages_depend_on(self, packages: List[Package], depends_on: Optional[Iterable[str]]) -> List[Package]:
        """
        extract list of packages which depends on specified package

        Args:
            packages(List[Package]): list of packages to be filtered
            depends_on(Optional[Iterable[str]]): dependencies of the packages

        Returns:
            List[Package]: list of repository packages which depend on specified packages
        """
        if depends_on is None:
            return packages  # no list provided extract everything by default
        depends_on = set(depends_on)

        return [
            package
            for package in packages
            if depends_on.intersection(package.full_depends(self.pacman, packages))
        ]
