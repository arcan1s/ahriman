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
from collections.abc import Iterable
from pathlib import Path
from tempfile import TemporaryDirectory

from ahriman.core.build_tools.sources import Sources
from ahriman.core.repository.repository_properties import RepositoryProperties
from ahriman.core.util import package_like
from ahriman.models.changes import Changes
from ahriman.models.package import Package


class PackageInfo(RepositoryProperties):
    """
    handler for the package information
    """

    def load_archives(self, packages: Iterable[Path]) -> list[Package]:
        """
        load packages from list of archives

        Args:
            packages(Iterable[Path]): paths to package archives

        Returns:
            list[Package]: list of read packages
        """
        sources = {package.base: package.remote for package, _, in self.reporter.package_get(None)}

        result: dict[str, Package] = {}
        # we are iterating over bases, not single packages
        for full_path in packages:
            try:
                local = Package.from_archive(full_path, self.pacman)
                if (source := sources.get(local.base)) is not None:  # update source with remote
                    local.remote = source

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

    def package_changes(self, package: Package, last_commit_sha: str | None) -> Changes:
        """
        extract package change for the package since last commit if available

        Args:
            package(Package): package properties
            last_commit_sha(str | None): last known commit hash

        Returns:
            Changes: changes if available
        """
        with TemporaryDirectory(ignore_cleanup_errors=True) as dir_name:
            dir_path = Path(dir_name)
            patches = self.reporter.package_patches_get(package.base, None)
            current_commit_sha = Sources.load(dir_path, package, patches, self.paths)

            changes: str | None = None
            if current_commit_sha != last_commit_sha:
                changes = Sources.changes(dir_path, last_commit_sha)

            return Changes(last_commit_sha, changes)

    def packages(self, filter_packages: Iterable[str] | None = None) -> list[Package]:
        """
        generate list of repository packages

        Args:
            filter_packages(Iterable[str] | None, optional): filter packages list by specified only

        Returns:
            list[Package]: list of packages properties
        """
        packages = self.load_archives(filter(package_like, self.paths.repository.iterdir()))
        if filter_packages:
            packages = [package for package in packages if package.base in filter_packages]

        return packages

    def packages_built(self) -> list[Path]:
        """
        get list of files in built packages directory

        Returns:
            list[Path]: list of filenames from the directory
        """
        return list(filter(package_like, self.paths.packages.iterdir()))

    def packages_depend_on(self, packages: list[Package], depends_on: Iterable[str] | None) -> list[Package]:
        """
        extract list of packages which depends on specified package

        Args:
            packages(list[Package]): list of packages to be filtered
            depends_on(Iterable[str] | None): dependencies of the packages

        Returns:
            list[Package]: list of repository packages which depend on specified packages
        """
        if depends_on is None:
            return packages  # no list provided extract everything by default
        depends_on = set(depends_on)

        return [
            package
            for package in packages
            if depends_on.intersection(package.full_depends(self.pacman, packages))
        ]
