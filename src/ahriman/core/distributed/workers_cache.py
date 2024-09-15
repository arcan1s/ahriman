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
import time

from threading import Lock

from ahriman.core.configuration import Configuration
from ahriman.core.log import LazyLogging
from ahriman.models.worker import Worker


class WorkersCache(LazyLogging):
    """
    cached storage for healthy workers

    Attributes:
        time_to_live(int): maximal amount of time in seconds to keep worker alive
    """

    def __init__(self, configuration: Configuration) -> None:
        """
        Args:
            configuration(Configuration): configuration instance
        """
        self.time_to_live = configuration.getint("worker", "time_to_live", fallback=60)
        self._lock = Lock()
        self._workers: dict[str, tuple[Worker, float]] = {}

    @property
    def workers(self) -> list[Worker]:
        """
        extract currently healthy workers

        Returns:
            list[Worker]: list of currently registered workers which have been seen not earlier than :attr:`time_to_live`
        """
        valid_from = time.monotonic() - self.time_to_live
        with self._lock:
            return [
                worker
                for worker, last_seen in self._workers.values()
                if last_seen > valid_from
            ]

    def workers_remove(self) -> None:
        """
        remove all workers from the cache
        """
        with self._lock:
            self._workers = {}

    def workers_update(self, worker: Worker) -> None:
        """
        register or update remote worker

        Args:
            worker(Worker): worker to register
        """
        with self._lock:
            self._workers[worker.identifier] = (worker, time.monotonic())
