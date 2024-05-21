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

from ahriman.application.application.application_properties import ApplicationProperties
from ahriman.application.application.workers import Updater
from ahriman.core.build_tools.sources import Sources
from ahriman.models.package import Package
from ahriman.models.packagers import Packagers
from ahriman.models.result import Result


class ApplicationRepository(ApplicationProperties):
    """
    repository control class
    """

    def changes(self, packages: Iterable[Package]) -> None:
        """
        generate and update package changes

        Args:
            packages(Iterable[Package]): list of packages to retrieve changes
        """
        for package in packages:
            last_commit_sha = self.reporter.package_changes_get(package.base).last_commit_sha
            if last_commit_sha is None:
                continue  # skip check in case if we can't calculate diff

            changes = self.repository.package_changes(package, last_commit_sha)
            self.repository.reporter.package_changes_update(package.base, changes)

    def clean(self, *, cache: bool, chroot: bool, manual: bool, packages: bool, pacman: bool) -> None:
        """
        run all clean methods. Warning: some functions might not be available for non-root user

        Args:
            cache(bool): clear directory with package caches
            chroot(bool): clear build chroot
            manual(bool): clear directory with manually added packages' bases
            packages(bool): clear directory with built packages
            pacman(bool): clear directory with pacman databases
        """
        if cache:
            self.repository.clear_cache()
        if chroot:
            self.repository.clear_chroot()
        if manual:
            self.repository.clear_queue()
        if packages:
            self.repository.clear_packages()
        if pacman:
            self.repository.clear_pacman()

    def on_result(self, result: Result) -> None:
        """
        generate report and sync to remote server

        Args:
            result(Result): build result

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def sign(self, packages: Iterable[str]) -> None:
        """
        sign packages and repository

        Args:
            packages(Iterable[str]): only sign specified packages
        """
        # copy to prebuilt directory
        for package in self.repository.packages(packages):
            for archive in package.packages.values():
                if archive.filepath is None:
                    self.logger.warning("filepath is empty for %s", package.base)
                    continue  # avoid mypy warning
                self.repository.sign.process_sign_package(archive.filepath, None)
        # sign repository database if set
        self.repository.sign.process_sign_repository(self.repository.repo.repo_path)
        # process triggers
        self.on_result(Result())

    def unknown(self) -> list[str]:
        """
        get packages which were not found in AUR

        Returns:
            list[str]: unknown package archive list
        """
        def has_local(probe: Package) -> bool:
            cache_dir = self.repository.paths.cache_for(probe.base)
            return cache_dir.is_dir() and not Sources.has_remotes(cache_dir)

        def unknown_aur(probe: Package) -> list[str]:
            packages: list[str] = []
            for single in probe.packages:
                try:
                    _ = Package.from_aur(single, None)
                except Exception:
                    packages.append(single)
            return packages

        def unknown_local(probe: Package) -> list[str]:
            cache_dir = self.repository.paths.cache_for(probe.base)
            local = Package.from_build(cache_dir, self.architecture, None)
            packages = set(probe.packages.keys()).difference(local.packages.keys())
            return list(packages)

        result = []
        for package in self.repository.packages():
            if has_local(package):
                result.extend(unknown_local(package))  # there is local package
            else:
                result.extend(unknown_aur(package))  # local package not found
        return result

    def update(self, updates: Iterable[Package], packagers: Packagers | None = None, *,
               bump_pkgrel: bool = False) -> Result:
        """
        run package updates. This method will separate update in the several steps:

            #. Check already built packages.
            #. Construct builder instance.
            #. Delegate build process to the builder instance (either remote or local).

        Args:
            updates(Iterable[Package]): list of packages to update
            packagers(Packagers | None, optional): optional override of username for build process
                (Default value = None)
            bump_pkgrel(bool, optional): bump pkgrel in case of local version conflict (Default value = False)

        Returns:
            Result: update result
        """
        result = Result()

        # process already built packages if any
        built_packages = self.repository.packages_built()
        if built_packages:  # speedup a bit
            build_result = self.repository.process_update(built_packages, packagers)
            self.on_result(build_result)
            result.merge(build_result)

        builder = Updater.load(self.repository_id, self.configuration, self.repository)

        # ok so for now we split all packages into chunks and process each chunk accordingly
        partitions = builder.partition(updates)
        for num, partition in enumerate(partitions):
            self.logger.info("processing chunk #%i %s", num, [package.base for package in partition])
            build_result = builder.update(partition, packagers, bump_pkgrel=bump_pkgrel)
            self.on_result(build_result)
            result.merge(build_result)

        return result

    def updates(self, filter_packages: Iterable[str], *,
                aur: bool, local: bool, manual: bool, vcs: bool, check_files: bool) -> list[Package]:
        """
        get list of packages to run update process

        Args:
            filter_packages(Iterable[str]): do not check every package just specified in the list
            aur(bool): enable or disable checking for AUR updates
            local(bool): enable or disable checking of local packages for updates
            manual(bool): include or exclude manual updates
            vcs(bool): enable or disable checking of VCS packages
            check_files(bool): check for broken dependencies

        Returns:
            list[Package]: list of out-of-dated packages
        """
        updates = {}

        if aur:
            updates.update({package.base: package for package in self.repository.updates_aur(filter_packages, vcs=vcs)})
        if local:
            updates.update({package.base: package for package in self.repository.updates_local(vcs=vcs)})
        if manual:
            updates.update({package.base: package for package in self.repository.updates_manual()})
        if check_files:
            updates.update({package.base: package for package in self.repository.updates_dependencies(filter_packages)})

        return [package for _, package in sorted(updates.items())]
