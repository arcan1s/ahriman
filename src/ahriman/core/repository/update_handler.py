#
# Copyright (c) 2021 Evgenii Alekseev.
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
import os

from typing import Iterable, List

from ahriman.core.repository.cleaner import Cleaner
from ahriman.models.package import Package


class UpdateHandler(Cleaner):
    """
    trait to get package update list
    """

    def packages(self) -> List[Package]:
        """
        generate list of repository packages
        :return: list of packages properties
        """
        raise NotImplementedError

    def updates_aur(self, filter_packages: Iterable[str], no_vcs: bool) -> List[Package]:
        """
        check AUR for updates
        :param filter_packages: do not check every package just specified in the list
        :param no_vcs: do not check VCS packages
        :return: list of packages which are out-of-dated
        """
        result: List[Package] = []

        build_section = self.config.get_section_name("build", self.architecture)
        ignore_list = self.config.getlist(build_section, "ignore_packages")

        for local in self.packages():
            if local.base in ignore_list:
                continue
            if local.is_vcs and no_vcs:
                continue
            if filter_packages and local.base not in filter_packages:
                continue

            try:
                remote = Package.load(local.base, self.pacman, self.aur_url)
                if local.is_outdated(remote, self.paths):
                    self.reporter.set_pending(local.base)
                    result.append(remote)
            except Exception:
                self.reporter.set_failed(local.base)
                self.logger.exception(f"could not load remote package {local.base}", exc_info=True)
                continue

        return result

    def updates_manual(self) -> List[Package]:
        """
        check for packages for which manual update has been requested
        :return: list of packages which are out-of-dated
        """
        result: List[Package] = []
        known_bases = {package.base for package in self.packages()}

        for fn in os.listdir(self.paths.manual):
            try:
                local = Package.load(os.path.join(self.paths.manual, fn), self.pacman, self.aur_url)
                result.append(local)
                if local.base not in known_bases:
                    self.reporter.set_unknown(local)
                else:
                    self.reporter.set_pending(local.base)
            except Exception:
                self.logger.exception(f"could not add package from {fn}", exc_info=True)
        self.clear_manual()

        return result
