#
# Copyright (c) 2021 ahriman team.
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
import logging
import shutil

from pathlib import Path
from typing import Callable, Iterable, List, Set

from ahriman.core.build_tools.sources import Sources
from ahriman.core.configuration import Configuration
from ahriman.core.repository.repository import Repository
from ahriman.core.tree import Tree
from ahriman.core.util import package_like
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource


class Application:
    """
    base application class
    :ivar architecture: repository architecture
    :ivar configuration: configuration instance
    :ivar logger: application logger
    :ivar repository: repository instance
    """

    def __init__(self, architecture: str, configuration: Configuration, no_report: bool) -> None:
        """
        default constructor
        :param architecture: repository architecture
        :param configuration: configuration instance
        :param no_report: force disable reporting
        """
        self.logger = logging.getLogger("root")
        self.configuration = configuration
        self.architecture = architecture
        self.repository = Repository(architecture, configuration, no_report)

    def _finalize(self, built_packages: Iterable[Package]) -> None:
        """
        generate report and sync to remote server
        """
        self.report([], built_packages)
        self.sync([], built_packages)

    def _known_packages(self) -> Set[str]:
        """
        load packages from repository and pacman repositories
        :return: list of known packages
        """
        known_packages: Set[str] = set()
        # local set
        for base in self.repository.packages():
            for package, properties in base.packages.items():
                known_packages.add(package)
                known_packages.update(properties.provides)
        known_packages.update(self.repository.pacman.all_packages())
        return known_packages

    def get_updates(self, filter_packages: List[str], no_aur: bool, no_manual: bool, no_vcs: bool,
                    log_fn: Callable[[str], None]) -> List[Package]:
        """
        get list of packages to run update process
        :param filter_packages: do not check every package just specified in the list
        :param no_aur: do not check for aur updates
        :param no_manual: do not check for manual updates
        :param no_vcs: do not check VCS packages
        :param log_fn: logger function to log updates
        :return: list of out-of-dated packages
        """
        updates = []

        if not no_aur:
            updates.extend(self.repository.updates_aur(filter_packages, no_vcs))
        if not no_manual:
            updates.extend(self.repository.updates_manual())

        for package in updates:
            log_fn(f"{package.base} = {package.version}")

        return updates

    def add(self, names: Iterable[str], source: PackageSource, without_dependencies: bool) -> None:
        """
        add packages for the next build
        :param names: list of package bases to add
        :param source: package source to add
        :param without_dependencies: if set, dependency check will be disabled
        """
        known_packages = self._known_packages()
        aur_url = self.configuration.get("alpm", "aur_url")

        def add_archive(src: Path) -> None:
            dst = self.repository.paths.packages / src.name
            shutil.move(src, dst)

        def add_directory(path: Path) -> None:
            for full_path in filter(package_like, path.iterdir()):
                add_archive(full_path)

        def add_local(path: Path) -> Path:
            package = Package.load(path, self.repository.pacman, aur_url)
            cache_dir = self.repository.paths.cache_for(package.base)
            shutil.copytree(path, cache_dir)  # copy package to store in caches
            Sources.init(cache_dir)  # we need to run init command in directory where we do have permissions
            shutil.copytree(cache_dir, self.repository.paths.manual_for(package.base))  # copy package for the build
            return self.repository.paths.manual_for(package.base)

        def add_remote(src: str) -> Path:
            package = Package.load(src, self.repository.pacman, aur_url)
            Sources.load(self.repository.paths.manual_for(package.base), package.git_url,
                         self.repository.paths.patches_for(package.base))
            return self.repository.paths.manual_for(package.base)

        def process_dependencies(path: Path) -> None:
            if without_dependencies:
                return
            dependencies = Package.dependencies(path)
            self.add(dependencies.difference(known_packages), PackageSource.AUR, without_dependencies)

        def process_single(src: str) -> None:
            resolved_source = source.resolve(src)
            if resolved_source == PackageSource.Archive:
                add_archive(Path(src))
            elif resolved_source == PackageSource.AUR:
                path = add_remote(src)
                process_dependencies(path)
            elif resolved_source == PackageSource.Directory:
                add_directory(Path(src))
            elif resolved_source == PackageSource.Local:
                path = add_local(Path(src))
                process_dependencies(path)

        for name in names:
            process_single(name)

    def clean(self, no_build: bool, no_cache: bool, no_chroot: bool, no_manual: bool, no_packages: bool) -> None:
        """
        run all clean methods. Warning: some functions might not be available under non-root
        :param no_build: do not clear directory with package sources
        :param no_cache: do not clear directory with package caches
        :param no_chroot: do not clear build chroot
        :param no_manual: do not clear directory with manually added packages
        :param no_packages: do not clear directory with built packages
        """
        if not no_build:
            self.repository.clear_build()
        if not no_cache:
            self.repository.clear_cache()
        if not no_chroot:
            self.repository.clear_chroot()
        if not no_manual:
            self.repository.clear_manual()
        if not no_packages:
            self.repository.clear_packages()

    def remove(self, names: Iterable[str]) -> None:
        """
        remove packages from repository
        :param names: list of packages (either base or name) to remove
        """
        self.repository.process_remove(names)
        self._finalize([])

    def report(self, target: Iterable[str], built_packages: Iterable[Package]) -> None:
        """
        generate report
        :param target: list of targets to run (e.g. html)
        :param built_packages: list of packages which has just been built
        """
        targets = target or None
        self.repository.process_report(targets, built_packages)

    def sign(self, packages: Iterable[str]) -> None:
        """
        sign packages and repository
        :param packages: only sign specified packages
        """
        # copy to prebuilt directory
        for package in self.repository.packages():
            # no one requested this package
            if packages and package.base not in packages:
                continue
            for archive in package.packages.values():
                if archive.filepath is None:
                    self.logger.warning("filepath is empty for %s", package.base)
                    continue  # avoid mypy warning
                src = self.repository.paths.repository / archive.filepath
                dst = self.repository.paths.packages / archive.filepath
                shutil.copy(src, dst)
        # run generic update function
        self.update([])
        # sign repository database if set
        self.repository.sign.sign_repository(self.repository.repo.repo_path)
        self._finalize([])

    def sync(self, target: Iterable[str], built_packages: Iterable[Package]) -> None:
        """
        sync to remote server
        :param target: list of targets to run (e.g. s3)
        :param built_packages: list of packages which has just been built
        """
        targets = target or None
        self.repository.process_sync(targets, built_packages)

    def unknown(self) -> List[Package]:
        """
        get packages which were not found in AUR
        :return: unknown package list
        """
        def has_aur(package_base: str, aur_url: str) -> bool:
            try:
                _ = Package.from_aur(package_base, aur_url)
            except Exception:
                return False
            return True

        def has_local(package_base: str) -> bool:
            cache_dir = self.repository.paths.cache_for(package_base)
            return cache_dir.is_dir() and not Sources.has_remotes(cache_dir)

        return [
            package
            for package in self.repository.packages()
            if not has_aur(package.base, package.aur_url) and not has_local(package.base)
        ]

    def update(self, updates: Iterable[Package]) -> None:
        """
        run package updates
        :param updates: list of packages to update
        """
        def process_update(paths: Iterable[Path]) -> None:
            if not paths:
                return  # don't need to process if no update supplied
            updated = [Package.load(path, self.repository.pacman, self.repository.aur_url) for path in paths]
            self.repository.process_update(paths)
            self._finalize(updated)

        # process built packages
        packages = self.repository.packages_built()
        process_update(packages)

        # process manual packages
        tree = Tree.load(updates, self.repository.paths)
        for num, level in enumerate(tree.levels()):
            self.logger.info("processing level #%i %s", num, [package.base for package in level])
            packages = self.repository.process_build(level)
            process_update(packages)
