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
import contextlib

from functools import cached_property

from ahriman.core.configuration import Configuration
from ahriman.core.status.web_client import WebClient
from ahriman.core.triggers import Trigger
from ahriman.models.repository_id import RepositoryId
from ahriman.models.worker import Worker


class DistributedSystem(Trigger, WebClient):
    """
    simple class to (un)register itself as a distributed worker
    """

    CONFIGURATION_SCHEMA = {
        "worker": {
            "type": "dict",
            "schema": {
                "address": {
                    "type": "string",
                    "required": True,
                    "empty": False,
                    "is_url": [],
                },
                "identifier": {
                    "type": "string",
                    "empty": False,
                },
                "time_to_live": {
                    "type": "integer",
                    "coerce": "integer",
                    "min": 1,
                },
            },
        },
    }

    def __init__(self, repository_id: RepositoryId, configuration: Configuration) -> None:
        """
        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
        """
        Trigger.__init__(self, repository_id, configuration)
        WebClient.__init__(self, repository_id, configuration)

    @cached_property
    def worker(self) -> Worker:
        """
        load and set worker. Lazy property loaded because it is not always required

        Returns:
            Worker: unique self worker identifier
        """
        section = next(iter(self.configuration_sections(self.configuration)))

        address = self.configuration.get(section, "address")
        identifier = self.configuration.get(section, "identifier", fallback="")
        return Worker(address, identifier=identifier)

    @classmethod
    def configuration_sections(cls, configuration: Configuration) -> list[str]:
        """
        extract configuration sections from configuration

        Args:
            configuration(Configuration): configuration instance

        Returns:
            list[str]: read configuration sections belong to this trigger
        """
        return list(cls.CONFIGURATION_SCHEMA.keys())

    def _workers_url(self) -> str:
        """
        workers url generator

        Returns:
            str: full url of web service for workers
        """
        return f"{self.address}/api/v1/distributed"

    def register(self) -> None:
        """
        register itself in remote system
        """
        with contextlib.suppress(Exception):
            self.make_request("POST", self._workers_url(), json=self.worker.view())

    def workers(self) -> list[Worker]:
        """
        retrieve list of available remote workers

        Returns:
            list[Worker]: currently registered workers
        """
        with contextlib.suppress(Exception):
            response = self.make_request("GET", self._workers_url())
            response_json = response.json()

            return [
                Worker(worker["address"], identifier=worker["identifier"])
                for worker in response_json
            ]

        return []
