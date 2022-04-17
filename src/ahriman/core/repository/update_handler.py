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
from typing import Iterable, List

from ahriman.core.build_tools.sources import Sources
from ahriman.core.repository.cleaner import Cleaner
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource


class UpdateHandler(Cleaner):
    """
    trait to get package update list
    """

    def packages(self) -> List[Package]:
        """
        generate list of repository packages

        Returns:
            List[Package]: list of packages properties

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def updates_aur(self, filter_packages: Iterable[str], no_vcs: bool) -> List[Package]:
        """
        check AUR for updates

        Args:
            filter_packages(Iterable[str]): do not check every package just specified in the list
            no_vcs(bool): do not check VCS packages

        Returns:
            List[Package]: list of packages which are out-of-dated
        """
        result: List[Package] = []

        for local in self.packages():
            if local.base in self.ignore_list:
                continue
            if local.is_vcs and no_vcs:
                continue
            if filter_packages and local.base not in filter_packages:
                continue

            try:
                remote = Package.load(local.base, PackageSource.AUR, self.pacman, self.aur_url)
                if local.is_outdated(remote, self.paths):
                    self.reporter.set_pending(local.base)
                    result.append(remote)
                self.reporter.set_success(local)
            except Exception:
                self.reporter.set_failed(local.base)
                self.logger.exception("could not load remote package %s", local.base)
                continue

        return result

    def updates_local(self) -> List[Package]:
        """
        check local packages for updates

        Returns:
            List[Package]: list of local packages which are out-of-dated
        """
        result: List[Package] = []
        packages = {local.base: local for local in self.packages()}

        for dirname in self.paths.cache.iterdir():
            try:
                Sources.fetch(dirname, remote=None)
                remote = Package.load(str(dirname), PackageSource.Local, self.pacman, self.aur_url)

                local = packages.get(remote.base)
                if local is None:
                    self.reporter.set_unknown(remote)
                    result.append(remote)
                elif local.is_outdated(remote, self.paths):
                    self.reporter.set_pending(local.base)
                    result.append(remote)
                else:
                    self.reporter.set_success(local)
            except Exception:
                self.logger.exception("could not process package at %s", dirname)

        return result

    def updates_manual(self) -> List[Package]:
        """
        check for packages for which manual update has been requested

        Returns:
            List[Package]: list of packages which are out-of-dated
        """
        result: List[Package] = []
        known_bases = {package.base for package in self.packages()}

        try:
            for local in self.database.build_queue_get():
                result.append(local)
                if local.base not in known_bases:
                    self.reporter.set_unknown(local)
                else:
                    self.reporter.set_pending(local.base)
        except Exception:
            self.logger.exception("could not load packages from database")
        self.clear_queue()

        return result
