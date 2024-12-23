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
from collections import deque
from collections.abc import Iterable

from ahriman.application.application.workers.updater import Updater
from ahriman.core.configuration import Configuration
from ahriman.core.http import SyncAhrimanClient
from ahriman.core.tree import Tree
from ahriman.models.package import Package
from ahriman.models.packagers import Packagers
from ahriman.models.repository_id import RepositoryId
from ahriman.models.result import Result
from ahriman.models.worker import Worker


class RemoteUpdater(Updater):
    """
    remote update worker

    Attributes:
        configuration(Configuration): configuration instance
        repository_id(RepositoryId): repository unique identifier
        workers(list[Worker]): worker identifiers
    """

    def __init__(self, workers: list[Worker], repository_id: RepositoryId, configuration: Configuration) -> None:
        """
        Args:
            workers(list[Worker]): worker identifiers
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
        """
        self.workers = workers
        self.repository_id = repository_id
        self.configuration = configuration

        self._clients: deque[tuple[Worker, SyncAhrimanClient]] = deque()

    @property
    def clients(self) -> dict[Worker, SyncAhrimanClient]:
        """
        extract loaded clients. Note that this method yields only workers which have been already loaded

        Returns:
            dict[Worker, SyncAhrimanClient]: map of the worker to the related web client
        """
        return dict(self._clients)

    @staticmethod
    def _update_url(worker: Worker) -> str:
        """
        get url for updates

        Args:
            worker(Worker): worker identifier

        Returns:
            str: full url for web service to run update process
        """
        return f"{worker.address}/api/v1/service/add"

    def next_worker(self) -> tuple[Worker, SyncAhrimanClient]:
        """
        generate next not-used web client. In case if all clients have been already used, it yields next not used client

        Returns:
            tuple[Worker, SyncAhrimanClient]: worker and constructed client instance for the web
        """
        # check if there is not used yet worker
        worker = next((worker for worker in self.workers if worker not in self.clients), None)
        if worker is not None:
            client = SyncAhrimanClient(self.configuration, "status")
            client.address = worker.address
        else:
            worker, client = self._clients.popleft()

        # register worker in the queue
        self._clients.append((worker, client))

        return worker, client

    def partition(self, packages: Iterable[Package]) -> list[list[Package]]:
        """
        split packages into partitions to be processed by this worker

        Args:
            packages(Iterable[Package]): list of packages to partition

        Returns:
            list[list[Package]]: packages partitioned by this worker type
        """
        return Tree.partition(packages, count=len(self.workers))

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
        payload = {
            "increment": False,  # force disable increment because it doesn't work yet
            "packager": packagers.default if packagers is not None else None,
            "packages": [package.base for package in updates],
            "patches": [],  # might be used later
            "refresh": True,
        }

        worker, client = self.next_worker()
        client.make_request("POST", self._update_url(worker), params=self.repository_id.query(), json=payload)
        # we don't block here for process

        return Result()
