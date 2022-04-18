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
import shutil

from pathlib import Path
from typing import Callable, Iterable, List

from ahriman.application.application.application_properties import ApplicationProperties
from ahriman.core.build_tools.sources import Sources
from ahriman.core.formatters.update_printer import UpdatePrinter
from ahriman.core.tree import Tree
from ahriman.models.package import Package
from ahriman.models.result import Result


class ApplicationRepository(ApplicationProperties):
    """
    repository control class
    """

    def _finalize(self, result: Result) -> None:
        """
        generate report and sync to remote server

        Args:
            result(Result): build result

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def clean(self, cache: bool, chroot: bool, manual: bool, packages: bool) -> None:
        """
        run all clean methods. Warning: some functions might not be available under non-root

        Args:
            cache(bool): clear directory with package caches
            chroot(bool): clear build chroot
            manual(bool): clear directory with manually added packages
            packages(bool): clear directory with built packages
        """
        if cache:
            self.repository.clear_cache()
        if chroot:
            self.repository.clear_chroot()
        if manual:
            self.repository.clear_queue()
        if packages:
            self.repository.clear_packages()

    def report(self, target: Iterable[str], result: Result) -> None:
        """
        generate report

        Args:
            target(Iterable[str]): list of targets to run (e.g. html)
            result(Result): build result
        """
        targets = target or None
        self.repository.process_report(targets, result)

    def sign(self, packages: Iterable[str]) -> None:
        """
        sign packages and repository

        Args:
            packages(Iterable[str]): only sign specified packages
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
        self._finalize(Result())

    def sync(self, target: Iterable[str], built_packages: Iterable[Package]) -> None:
        """
        sync to remote server

        Args:
            target(Iterable[str]): list of targets to run (e.g. s3)
            built_packages(Iterable[Package]): list of packages which has just been built
        """
        targets = target or None
        self.repository.process_sync(targets, built_packages)

    def unknown(self) -> List[str]:
        """
        get packages which were not found in AUR

        Returns:
            List[str]: unknown package archive list
        """
        def has_local(probe: Package) -> bool:
            cache_dir = self.repository.paths.cache_for(probe.base)
            return cache_dir.is_dir() and not Sources.has_remotes(cache_dir)

        def unknown_aur(probe: Package) -> List[str]:
            packages: List[str] = []
            for single in probe.packages:
                try:
                    _ = Package.from_aur(single, probe.aur_url)
                except Exception:
                    packages.append(single)
            return packages

        def unknown_local(probe: Package) -> List[str]:
            cache_dir = self.repository.paths.cache_for(probe.base)
            local = Package.from_build(cache_dir, probe.aur_url)
            packages = set(probe.packages.keys()).difference(local.packages.keys())
            return list(packages)

        result = []
        for package in self.repository.packages():
            if has_local(package):
                result.extend(unknown_local(package))  # there is local package
            else:
                result.extend(unknown_aur(package))  # local package not found
        return result

    def update(self, updates: Iterable[Package]) -> Result:
        """
        run package updates

        Args:
            updates(Iterable[Package]): list of packages to update

        Returns:
            Result: update result
        """
        def process_update(paths: Iterable[Path], result: Result) -> None:
            if not paths:
                return  # don't need to process if no update supplied
            update_result = self.repository.process_update(paths)
            self._finalize(result.merge(update_result))

        # process built packages
        build_result = Result()
        packages = self.repository.packages_built()
        process_update(packages, build_result)

        # process manual packages
        tree = Tree.load(updates, self.database)
        for num, level in enumerate(tree.levels()):
            self.logger.info("processing level #%i %s", num, [package.base for package in level])
            build_result = self.repository.process_build(level)
            packages = self.repository.packages_built()
            process_update(packages, build_result)

        return build_result

    def updates(self, filter_packages: Iterable[str], no_aur: bool, no_local: bool, no_manual: bool, no_vcs: bool,
                log_fn: Callable[[str], None]) -> List[Package]:
        """
        get list of packages to run update process

        Args:
            filter_packages(Iterable[str]): do not check every package just specified in the list
            no_aur(bool): do not check for aur updates
            no_local(bool): do not check local packages for updates
            no_manual(bool): do not check for manual updates
            no_vcs(bool): do not check VCS packages
            log_fn(Callable[[str], None]): logger function to log updates

        Returns:
            List[Package]: list of out-of-dated packages
        """
        updates = {}

        if not no_aur:
            updates.update({package.base: package for package in self.repository.updates_aur(filter_packages, no_vcs)})
        if not no_local:
            updates.update({package.base: package for package in self.repository.updates_local()})
        if not no_manual:
            updates.update({package.base: package for package in self.repository.updates_manual()})

        local_versions = {package.base: package.version for package in self.repository.packages()}
        updated_packages = [package for _, package in sorted(updates.items())]
        for package in updated_packages:
            UpdatePrinter(package, local_versions.get(package.base)).print(
                verbose=True, log_fn=log_fn, separator=" -> ")

        return updated_packages
