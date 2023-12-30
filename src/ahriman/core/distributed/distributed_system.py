#
# Copyright (c) 2021-2023 ahriman team.
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
import tempfile
import uuid

from pathlib import Path

from ahriman.core.configuration import Configuration
from ahriman.core.configuration.schema import ConfigurationSchema
from ahriman.core.status.web_client import WebClient
from ahriman.core.triggers import Trigger
from ahriman.models.repository_id import RepositoryId
from ahriman.models.worker import Worker


class DistributedSystem(Trigger, WebClient):
    """
    simple class to (un)register itself as a distributed worker

    Attributes:
        identifier_path(Path): path to cached worker identifier
        worker(Worker): unique self identifier
    """

    CONFIGURATION_SCHEMA: ConfigurationSchema = {
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
                "identifier_path": {
                    "type": "path",
                    "coerce": "absolute_path",
                },
            },
        },
    }

    def __init__(self, repository_id: RepositoryId, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
        """
        Trigger.__init__(self, repository_id, configuration)
        WebClient.__init__(self, repository_id, configuration)

        section = next(iter(self.configuration_sections(configuration)))
        self.identifier_path = configuration.getpath(
            section, "identifier_path", fallback=Path(tempfile.gettempdir()) / "ahriman-worker-identifier")
        self._owe_identifier = False

        identifier = self.load_identifier(configuration, section)
        self.worker = Worker(configuration.get(section, "address"), identifier=identifier)

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

    def _workers_url(self, identifier: str = "") -> str:
        """
        workers url generator

        Args:
            identifier(str, optional): worker identifier (Default value = "")

        Returns:
            str: full url of web service for specific worker
        """
        suffix = f"/{identifier}" if identifier else ""
        return f"{self.address}/api/v1/distributed{suffix}"

    def load_identifier(self, configuration: Configuration, section: str) -> str:
        """
        load identifier from filesystem if available or from configuration otherwise. If cache file is available,
        the method will read from it. Otherwise, it will try to read it from configuration. And, finally, if no
        identifier set, it will generate uuid

        Args:
            configuration(Configuration): configuration instance
            section(str): settings section name

        Returns:
            str: unique worker identifier
        """
        if self.identifier_path.is_file():  # load cached value
            return self.identifier_path.read_text(encoding="utf8")
        return configuration.get(section, "identifier", fallback=str(uuid.uuid4()))

    def register(self, force: bool = False) -> None:
        """
        register itself in remote system

        Args:
            force(bool, optional): register worker even if it has been already registered before (Default value = False)
        """
        if self.identifier_path.is_file() and not force:
            return  # there is already registered identifier

        self.make_request("POST", self._workers_url(), json=self.worker.view())
        # save identifier
        self.identifier_path.write_text(self.worker.identifier, encoding="utf8")
        self._owe_identifier = True
        self.logger.info("registered instance %s at %s", self.worker, self.address)

    def unregister(self, force: bool = False) -> None:
        """
        unregister itself in remote system

        Args:
            force(bool, optional): unregister worker even if it has been registered in another process
                (Default value = False)
        """
        if not self._owe_identifier and not force:
            return  # we do not owe this identifier

        self.make_request("DELETE", self._workers_url(self.worker.identifier))
        self.identifier_path.unlink(missing_ok=True)
        self.logger.info("unregistered instance %s at %s", self.worker, self.address)

    def workers(self) -> list[Worker]:
        """
        retrieve list of available remote workers

        Returns:
            list[Worker]: currently registered workers
        """
        response = self.make_request("GET", self._workers_url())
        response_json = response.json()

        return [
            Worker(worker["address"], identifier=worker["identifier"])
            for worker in response_json
        ]
