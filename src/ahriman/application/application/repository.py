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
import shutil

from pathlib import Path
from typing import Callable, Iterable, List

from ahriman.application.application.properties import Properties
from ahriman.core.build_tools.sources import Sources
from ahriman.core.tree import Tree
from ahriman.models.package import Package


class Repository(Properties):
    """
    repository control class
    """

    def _finalize(self, built_packages: Iterable[Package]) -> None:
        """
        generate report and sync to remote server
        """
        raise NotImplementedError

    def clean(self, build: bool, cache: bool, chroot: bool, manual: bool, packages: bool, patches: bool) -> None:
        """
        run all clean methods. Warning: some functions might not be available under non-root
        :param build: clear directory with package sources
        :param cache: clear directory with package caches
        :param chroot: clear build chroot
        :param manual: clear directory with manually added packages
        :param packages: clear directory with built packages
        :param patches: clear directory with patches
        """
        if build:
            self.repository.clear_build()
        if cache:
            self.repository.clear_cache()
        if chroot:
            self.repository.clear_chroot()
        if manual:
            self.repository.clear_manual()
        if packages:
            self.repository.clear_packages()
        if patches:
            self.repository.clear_patches()

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
        self.repository.sign.process_sign_repository(self.repository.repo.repo_path)
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

    def updates(self, filter_packages: Iterable[str], no_aur: bool, no_manual: bool, no_vcs: bool,
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