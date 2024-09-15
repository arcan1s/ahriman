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
        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
        """
        DistributedSystem.__init__(self, repository_id, configuration)

        section = next(iter(self.configuration_sections(configuration)))
        self.ping_interval = configuration.getint(section, "time_to_live", fallback=60) / 4.0

        self._lock = Lock()
        self._timer: Timer | None = None

    def create_timer(self) -> None:
        """
        create timer object and put it to queue
        """
        self._timer = Timer(self.ping_interval, self.ping)
        self._timer.start()

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
            if self._timer is None:
                return

            self._timer.cancel()  # cancel remaining timers
            self._timer = None  # reset state

    def ping(self) -> None:
        """
        register itself as alive worker and update the timer
        """
        with self._lock:
            if self._timer is None:  # no active timer set, exit loop
                return

            self.register()
            self.create_timer()
