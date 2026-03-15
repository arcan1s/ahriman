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
import copy

from collections.abc import Callable, Iterable
from functools import cmp_to_key
from pathlib import Path
from tempfile import TemporaryDirectory

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.build_tools.package_version import PackageVersion
from ahriman.core.build_tools.sources import Sources
from ahriman.core.configuration import Configuration
from ahriman.core.log import LazyLogging
from ahriman.core.status import Client
from ahriman.core.utils import list_flatmap, package_like
from ahriman.models.changes import Changes
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId
from ahriman.models.repository_paths import RepositoryPaths


class PackageInfo(LazyLogging):
    """
    handler for the package information

    Attributes:
        configuration(Configuration): configuration instance
        pacman(Pacman): alpm wrapper instance
        paths(RepositoryPaths): repository paths instance
        reporter(Client): build status reporter instance
        repository_id(RepositoryId): repository unique identifier
    """

    configuration: Configuration
    pacman: Pacman
    paths: RepositoryPaths
    reporter: Client
    repository_id: RepositoryId

    def full_depends(self, package: Package, packages: Iterable[Package]) -> list[str]:
        """
        generate full dependencies list including transitive dependencies

        Args:
            package(Package): package to check dependencies for
            packages(Iterable[Package]): repository package list

        Returns:
            list[str]: all dependencies of the package
        """
        dependencies = {}
        # load own package dependencies
        for package_base in packages:
            for name, repo_package in package_base.packages.items():
                dependencies[name] = repo_package.depends
                for provides in repo_package.provides:
                    dependencies[provides] = repo_package.depends
        # load repository dependencies
        for database in self.pacman.handle.get_syncdbs():
            for pacman_package in database.pkgcache:
                dependencies[pacman_package.name] = pacman_package.depends
                for provides in pacman_package.provides:
                    dependencies[provides] = pacman_package.depends

        result = set(package.depends)
        current_depends: set[str] = set()
        while result != current_depends:
            current_depends = copy.deepcopy(result)
            for package_name in current_depends:
                result.update(dependencies.get(package_name, []))

        return sorted(result)

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
                local = Package.from_archive(full_path)
                if (source := sources.get(local.base)) is not None:  # update source with remote
                    local.remote = source

                current = result.setdefault(local.base, local)
                if current.version != local.version:
                    # force version to max of them
                    self.logger.warning("version of %s differs, found %s and %s",
                                        current.base, current.version, local.version)
                    if PackageVersion(current).is_outdated(local, self.configuration, calculate_version=False):
                        current.version = local.version
                current.packages.update(local.packages)
            except Exception:
                self.logger.exception("could not load package from %s", full_path)
        return list(result.values())

    def package_archives(self, package_base: str) -> list[Package]:
        """
        load list of packages known for this package base. This method unlike
        :func:`ahriman.core.repository.package_info.PackageInfo.load_archives` scans archive directory and loads all
        versions available for the ``package_base``

        Args:
            package_base(str): package base

        Returns:
            list[Package]: list of packages belonging to this base, sorted by version by ascension
        """
        packages: dict[tuple[str, str], Package] = {}
        # we can't use here load_archives, because it ignores versions
        for full_path in filter(package_like, self.paths.archive_for(package_base).iterdir()):
            local = Package.from_archive(full_path)
            if not local.supports_architecture(self.repository_id.architecture):
                continue
            packages.setdefault((local.base, local.version), local).packages.update(local.packages)

        comparator: Callable[[Package, Package], int] = lambda left, right: left.vercmp(right.version)
        return sorted(packages.values(), key=cmp_to_key(comparator))

    def package_archives_lookup(self, package: Package) -> list[Path]:
        """
        check if there is a rebuilt package already

        Args:
            package(Package): package to check

        Returns:
            list[Path]: list of built packages and signatures if available, empty list otherwise
        """
        archive = self.paths.archive_for(package.base)
        if not archive.is_dir():
            return []

        for path in filter(package_like, archive.iterdir()):
            # check if package version is the same
            built = Package.from_archive(path)
            if built.version != package.version:
                continue

            # all packages must be either any or same architecture
            if not built.supports_architecture(self.repository_id.architecture):
                continue

            return list_flatmap(built.packages.values(), lambda single: archive.glob(f"{single.filename}*"))

        return []

    def package_changes(self, package: Package, last_commit_sha: str) -> Changes | None:
        """
        extract package change for the package since last commit if available

        Args:
            package(Package): package properties
            last_commit_sha(str): last known commit hash

        Returns:
            Changes | None: changes if available
        """
        with TemporaryDirectory(ignore_cleanup_errors=True) as dir_name:
            dir_path = Path(dir_name)
            patches = self.reporter.package_patches_get(package.base, None)
            current_commit_sha = Sources.load(dir_path, package, patches, self.paths)

            if current_commit_sha != last_commit_sha:
                return Sources.changes(dir_path, last_commit_sha)
            return None

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
            if depends_on.intersection(self.full_depends(package, packages))
        ]
