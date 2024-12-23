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
from __future__ import annotations

from collections.abc import Iterable

from ahriman.core.configuration import Configuration
from ahriman.core.log import LazyLogging
from ahriman.core.repository import Repository
from ahriman.models.package import Package
from ahriman.models.packagers import Packagers
from ahriman.models.repository_id import RepositoryId
from ahriman.models.result import Result
from ahriman.models.worker import Worker


class Updater(LazyLogging):
    """
    updater handler interface
    """

    @staticmethod
    def load(repository_id: RepositoryId, configuration: Configuration,
             repository: Repository, workers: list[Worker] | None = None) -> Updater:
        """
        construct updaters from parameters

        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            repository(Repository): repository instance
            workers(list[Worker] | None, optional): worker identifiers if any (Default value = None)

        Returns:
            Updater: constructed updater worker
        """
        if workers is None:
            # no workers set explicitly, try to guess from configuration
            workers = [Worker(address) for address in configuration.getlist("build", "workers", fallback=[])]

        if workers:
            # there is something we could use as remote workers
            from ahriman.application.application.workers.remote_updater import RemoteUpdater
            return RemoteUpdater(workers, repository_id, configuration)

        # and finally no workers available, just use local service
        from ahriman.application.application.workers.local_updater import LocalUpdater
        return LocalUpdater(repository)

    def partition(self, packages: Iterable[Package]) -> list[list[Package]]:
        """
        split packages into partitions to be processed by this worker

        Args:
            packages(Iterable[Package]): list of packages to partition

        Returns:
            list[list[Package]]: packages partitioned by this worker type

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

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

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError
