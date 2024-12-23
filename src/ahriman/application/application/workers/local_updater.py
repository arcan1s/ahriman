#
# Copyright (c) 2021-2025 ahriman team.
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

from ahriman.application.application.workers.updater import Updater
from ahriman.core.repository import Repository
from ahriman.core.tree import Tree
from ahriman.models.package import Package
from ahriman.models.packagers import Packagers
from ahriman.models.result import Result


class LocalUpdater(Updater):
    """
    local build process implementation

    Attributes:
        repository(Repository): repository instance
    """

    def __init__(self, repository: Repository) -> None:
        """
        Args:
            repository(Repository): repository instance
        """
        self.repository = repository

    def partition(self, packages: Iterable[Package]) -> list[list[Package]]:
        """
        split packages into partitions to be processed by this worker

        Args:
            packages(Iterable[Package]): list of packages to partition

        Returns:
            list[list[Package]]: packages partitioned by this worker type
        """
        return Tree.resolve(packages)

    def update(self, updates: Iterable[Package], packagers: Packagers | None = None, *,
               bump_pkgrel: bool = False) -> Result:
        """
        run package updates

        Args:
            updates(Iterable[Package]): list of packages to update
            packagers(Packagers | None, optional): optional override of username for build process
                (Default value = None)
            bump_pkgrel(bool, optional): bump pkgrel in case of local version conflict (Default value = False)

        Returns:
            Result: update result
        """
        build_result = self.repository.process_build(updates, packagers, bump_pkgrel=bump_pkgrel)
        packages = self.repository.packages_built()
        update_result = self.repository.process_update(packages, packagers)

        return build_result.merge(update_result)
