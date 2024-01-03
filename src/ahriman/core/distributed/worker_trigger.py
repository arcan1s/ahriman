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
from collections import deque
from threading import Lock, Timer

from ahriman.core.configuration import Configuration
from ahriman.core.distributed.distributed_system import DistributedSystem
from ahriman.models.repository_id import RepositoryId


class WorkerTrigger(DistributedSystem):
    """
    remote worker processor trigger (client side)

    Attributes:
        ping_interval(float): interval to call remote service in seconds, defined as ``worker.time_to_live / 4``
    """

    def __init__(self, repository_id: RepositoryId, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
        """
        DistributedSystem.__init__(self, repository_id, configuration)

        section = next(iter(self.configuration_sections(configuration)))
        self.ping_interval = configuration.getint(section, "time_to_live", fallback=60) / 4.0

        self._lock = Lock()
        self._timers: deque[Timer] = deque()  # because python doesn't have atomics

    def create_timer(self) -> None:
        """
        create timer object and put it to queue
        """
        timer = Timer(self.ping_interval, self.ping)
        timer.start()
        self._timers.append(timer)

    def on_start(self) -> None:
        """
        trigger action which will be called at the start of the application
        """
        self.logger.info("registering instance %s in %s", self.worker, self.address)
        with self._lock:
            self.create_timer()

    def on_stop(self) -> None:
        """
        trigger action which will be called before the stop of the application
        """
        self.logger.info("removing instance %s in %s", self.worker, self.address)
        with self._lock:
            current_timers = self._timers.copy()  # will be used later
            self._timers.clear()  # clear timer list

        for timer in current_timers:
            timer.cancel()  # cancel remaining timers

    def ping(self) -> None:
        """
        register itself as alive worker and update the timer
        """
        with self._lock:
            if not self._timers:  # make sure that there is related specific timer
                return

            self._timers.popleft()  # pop first timer

            self.register()
            self.create_timer()
