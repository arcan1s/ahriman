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
import contextlib
import logging

from urllib.parse import quote_plus as urlencode

from ahriman.core.configuration import Configuration
from ahriman.core.http import SyncAhrimanClient
from ahriman.core.status.client import Client
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.changes import Changes
from ahriman.models.internal_status import InternalStatus
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId


class WebClient(Client, SyncAhrimanClient):
    """
    build status reporter web client

    Attributes:
        repository_id(RepositoryId): repository unique identifier
    """

    def __init__(self, repository_id: RepositoryId, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
        """
        section, self.address = self.parse_address(configuration)
        suppress_errors = configuration.getboolean(  # read old-style first and then fallback to new style
            "settings", "suppress_http_log_errors",
            fallback=configuration.getboolean("status", "suppress_http_log_errors", fallback=False))
        SyncAhrimanClient.__init__(self, configuration, section, suppress_errors=suppress_errors)

        self.repository_id = repository_id

    @staticmethod
    def parse_address(configuration: Configuration) -> tuple[str, str]:
        """
        parse address from legacy configuration

        Args:
            configuration(Configuration): configuration instance

        Returns:
            tuple[str, str]: tuple of section name and server address
        """
        # new-style section
        if (address := configuration.get("status", "address", fallback=None)) is not None:
            return "status", address

        # legacy-style section
        if (unix_socket := configuration.get("web", "unix_socket", fallback=None)) is not None:
            # special pseudo-protocol which is used for unix sockets
            return "web", f"http+unix://{urlencode(unix_socket)}"
        address = configuration.get("web", "address", fallback=None)
        if not address:
            # build address from host and port directly
            host = configuration.get("web", "host")
            port = configuration.getint("web", "port")
            address = f"http://{host}:{port}"
        return "web", address

    def _changes_url(self, package_base: str) -> str:
        """
        get url for the changes api

        Args:
            package_base(str): package base

        Returns:
            str: full url for web service for logs
        """
        return f"{self.address}/api/v1/packages/{package_base}/changes"

    def _logs_url(self, package_base: str) -> str:
        """
        get url for the logs api

        Args:
            package_base(str): package base

        Returns:
            str: full url for web service for logs
        """
        return f"{self.address}/api/v1/packages/{package_base}/logs"

    def _package_url(self, package_base: str = "") -> str:
        """
        url generator

        Args:
            package_base(str, optional): package base to generate url (Default value = "")

        Returns:
            str: full url of web service for specific package base
        """
        suffix = f"/{package_base}" if package_base else ""
        return f"{self.address}/api/v1/packages{suffix}"

    def _status_url(self) -> str:
        """
        get url for the status api

        Returns:
            str: full url for web service for status
        """
        return f"{self.address}/api/v1/status"

    def package_add(self, package: Package, status: BuildStatusEnum) -> None:
        """
        add new package with status

        Args:
            package(Package): package properties
            status(BuildStatusEnum): current package build status
        """
        payload = {
            "status": status.value,
            "package": package.view()
        }
        with contextlib.suppress(Exception):
            self.make_request("POST", self._package_url(package.base),
                              params=self.repository_id.query(), json=payload)

    def package_changes_get(self, package_base: str) -> Changes:
        """
        get package changes

        Args:
            package_base(str): package base to retrieve

        Returns:
            Changes: package changes if available and empty object otherwise
        """
        with contextlib.suppress(Exception):
            response = self.make_request("GET", self._changes_url(package_base),
                                         params=self.repository_id.query())
            response_json = response.json()

            return Changes.from_json(response_json)

        return Changes()

    def package_changes_set(self, package_base: str, changes: Changes) -> None:
        """
        update package changes

        Args:
            package_base(str): package base to update
            changes(Changes): changes descriptor
        """
        with contextlib.suppress(Exception):
            self.make_request("POST", self._changes_url(package_base),
                              params=self.repository_id.query(), json=changes.view())

    def package_get(self, package_base: str | None) -> list[tuple[Package, BuildStatus]]:
        """
        get package status

        Args:
            package_base(str | None): package base to get

        Returns:
            list[tuple[Package, BuildStatus]]: list of current package description and status if it has been found
        """
        with contextlib.suppress(Exception):
            response = self.make_request("GET", self._package_url(package_base or ""),
                                         params=self.repository_id.query())
            response_json = response.json()

            return [
                (Package.from_json(package["package"]), BuildStatus.from_json(package["status"]))
                for package in response_json
            ]

        return []

    def package_logs(self, log_record_id: LogRecordId, record: logging.LogRecord) -> None:
        """
        post log record

        Args:
            log_record_id(LogRecordId): log record id
            record(logging.LogRecord): log record to post to api
        """
        payload = {
            "created": record.created,
            "message": record.getMessage(),
            "version": log_record_id.version,
        }

        # this is special case, because we would like to do not suppress exception here
        # in case of exception raised it will be handled by upstream HttpLogHandler
        # In the other hand, we force to suppress all http logs here to avoid cyclic reporting
        self.make_request("POST", self._logs_url(log_record_id.package_base),
                          params=self.repository_id.query(), json=payload, suppress_errors=True)

    def package_remove(self, package_base: str) -> None:
        """
        remove packages from watcher

        Args:
            package_base(str): basename to remove
        """
        with contextlib.suppress(Exception):
            self.make_request("DELETE", self._package_url(package_base), params=self.repository_id.query())

    def package_update(self, package_base: str, status: BuildStatusEnum) -> None:
        """
        update package build status. Unlike :func:`package_add()` it does not update package properties

        Args:
            package_base(str): package base to update
            status(BuildStatusEnum): current package build status
        """
        payload = {"status": status.value}
        with contextlib.suppress(Exception):
            self.make_request("POST", self._package_url(package_base),
                              params=self.repository_id.query(), json=payload)

    def status_get(self) -> InternalStatus:
        """
        get internal service status

        Returns:
            InternalStatus: current internal (web) service status
        """
        with contextlib.suppress(Exception):
            response = self.make_request("GET", self._status_url(), params=self.repository_id.query())
            response_json = response.json()

            return InternalStatus.from_json(response_json)

        return InternalStatus(status=BuildStatus())

    def status_update(self, status: BuildStatusEnum) -> None:
        """
        update ahriman status itself

        Args:
            status(BuildStatusEnum): current ahriman status
        """
        payload = {"status": status.value}
        with contextlib.suppress(Exception):
            self.make_request("POST", self._status_url(), params=self.repository_id.query(), json=payload)
