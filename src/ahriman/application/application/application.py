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
from typing import Iterable, Set

from ahriman.application.application.packages import Packages
from ahriman.application.application.repository import Repository
from ahriman.models.package import Package


class Application(Packages, Repository):
    """
    base application class
    """

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
