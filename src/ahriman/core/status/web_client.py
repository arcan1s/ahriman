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

from urllib.parse import quote_plus as urlencode

from ahriman.core.configuration import Configuration
from ahriman.core.http import SyncAhrimanClient
from ahriman.core.status import Client
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.changes import Changes
from ahriman.models.dependencies import Dependencies
from ahriman.models.event import Event, EventType
from ahriman.models.internal_status import InternalStatus
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.repository_id import RepositoryId


class WebClient(Client, SyncAhrimanClient):
    """
    build status reporter web client

    Attributes:
        repository_id(RepositoryId): repository unique identifier
    """

    def __init__(self, repository_id: RepositoryId, configuration: Configuration) -> None:
        """
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
            str: full url for web service for changes
        """
        return f"{self.address}/api/v1/packages/{urlencode(package_base)}/changes"

    def _dependencies_url(self, package_base: str) -> str:
        """
        get url for the dependencies api

        Args:
            package_base(str): package base

        Returns:
            str: full url for web service for dependencies
        """
        return f"{self.address}/api/v1/packages/{urlencode(package_base)}/dependencies"

    def _events_url(self) -> str:
        """
        get url for the events api

        Returns:
            str: full url for web service for events
        """
        return f"{self.address}/api/v1/events"

    def _logs_url(self, package_base: str) -> str:
        """
        get url for the logs api

        Args:
            package_base(str): package base

        Returns:
            str: full url for web service for logs
        """
        return f"{self.address}/api/v1/packages/{urlencode(package_base)}/logs"

    def _package_url(self, package_base: str = "") -> str:
        """
        package url generator

        Args:
            package_base(str, optional): package base to generate url (Default value = "")

        Returns:
            str: full url of web service for specific package base
        """
        suffix = f"/{urlencode(package_base)}" if package_base else ""
        return f"{self.address}/api/v1/packages{suffix}"

    def _patches_url(self, package_base: str, variable: str = "") -> str:
        """
        patches url generator

        Args:
            package_base(str): package base
            variable(str, optional): patch variable name to generate url (Default value = "")

        Returns:
            str: full url of web service for the package patch
        """
        suffix = f"/{urlencode(variable)}" if variable else ""
        return f"{self.address}/api/v1/packages/{urlencode(package_base)}/patches{suffix}"

    def _status_url(self) -> str:
        """
        get url for the status api

        Returns:
            str: full url for web service for status
        """
        return f"{self.address}/api/v1/status"

    def event_add(self, event: Event) -> None:
        """
        create new event

        Args:
            event(Event): audit log event
        """
        with contextlib.suppress(Exception):
            self.make_request("POST", self._events_url(), params=self.repository_id.query(), json=event.view())

    def event_get(self, event: str | EventType | None, object_id: str | None,
                  from_date: int | float | None = None, to_date: int | float | None = None,
                  limit: int = -1, offset: int = 0) -> list[Event]:
        """
        retrieve list of events

        Args:
            event(str | EventType | None): filter by event type
            object_id(str | None): filter by event object
            from_date(int | float | None, optional): minimal creation date, inclusive (Default value = None)
            to_date(int | float | None, optional): maximal creation date, exclusive (Default value = None)
            limit(int, optional): limit records to the specified count, -1 means unlimited (Default value = -1)
            offset(int, optional): records offset (Default value = 0)

        Returns:
            list[Event]: list of audit log events
        """
        query = self.repository_id.query() + [("limit", str(limit)), ("offset", str(offset))]
        if event is not None:
            query.append(("event", str(event)))
        if object_id is not None:
            query.append(("object_id", object_id))
        if from_date is not None:
            query.append(("from_date", str(from_date)))
        if to_date is not None:
            query.append(("to_date", str(to_date)))

        with contextlib.suppress(Exception):
            response = self.make_request("GET", self._events_url(), params=query)
            response_json = response.json()

            return [Event.from_json(event) for event in response_json]

        return []

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

    def package_changes_update(self, package_base: str, changes: Changes) -> None:
        """
        update package changes

        Args:
            package_base(str): package base to update
            changes(Changes): changes descriptor
        """
        with contextlib.suppress(Exception):
            self.make_request("POST", self._changes_url(package_base),
                              params=self.repository_id.query(), json=changes.view())

    def package_dependencies_get(self, package_base: str) -> Dependencies:
        """
        get package dependencies

        Args:
            package_base(str): package base to retrieve

        Returns:
            list[Dependencies]: package implicit dependencies if available
        """
        with contextlib.suppress(Exception):
            response = self.make_request("GET", self._dependencies_url(package_base),
                                         params=self.repository_id.query())
            response_json = response.json()

            return Dependencies.from_json(response_json)

        return Dependencies()

    def package_dependencies_update(self, package_base: str, dependencies: Dependencies) -> None:
        """
        update package dependencies

        Args:
            package_base(str): package base to update
            dependencies(Dependencies): dependencies descriptor
        """
        with contextlib.suppress(Exception):
            self.make_request("POST", self._dependencies_url(package_base),
                              params=self.repository_id.query(), json=dependencies.view())

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

    def package_logs_add(self, log_record_id: LogRecordId, created: float, message: str) -> None:
        """
        post log record

        Args:
            log_record_id(LogRecordId): log record id
            created(float): log created timestamp
            message(str): log message
        """
        payload = {
            "created": created,
            "message": message,
            "version": log_record_id.version,
        }

        # this is special case, because we would like to do not suppress exception here
        # in case of exception raised it will be handled by upstream HttpLogHandler
        # In the other hand, we force to suppress all http logs here to avoid cyclic reporting
        self.make_request("POST", self._logs_url(log_record_id.package_base),
                          params=self.repository_id.query(), json=payload, suppress_errors=True)

    def package_logs_get(self, package_base: str, limit: int = -1, offset: int = 0) -> list[tuple[float, str]]:
        """
        get package logs

        Args:
            package_base(str): package base
            limit(int, optional): limit records to the specified count, -1 means unlimited (Default value = -1)
            offset(int, optional): records offset (Default value = 0)

        Returns:
            list[tuple[float, str]]: package logs
        """
        query = self.repository_id.query() + [("limit", str(limit)), ("offset", str(offset))]

        with contextlib.suppress(Exception):
            response = self.make_request("GET", self._logs_url(package_base), params=query)
            response_json = response.json()

            return [(record["created"], record["message"]) for record in response_json]

        return []

    def package_logs_remove(self, package_base: str, version: str | None) -> None:
        """
        remove package logs

        Args:
            package_base(str): package base
            version(str | None): package version to remove logs. If ``None`` is set, all logs will be removed
        """
        query = self.repository_id.query()
        if version is not None:
            query += [("version", version)]

        with contextlib.suppress(Exception):
            self.make_request("DELETE", self._logs_url(package_base), params=query)

    def package_patches_get(self, package_base: str, variable: str | None) -> list[PkgbuildPatch]:
        """
        get package patches

        Args:
            package_base(str): package base to retrieve
            variable(str | None): optional filter by patch variable

        Returns:
            list[PkgbuildPatch]: list of patches for the specified package
        """
        with contextlib.suppress(Exception):
            response = self.make_request("GET", self._patches_url(package_base, variable or ""))
            response_json = response.json()

            patches = response_json if variable is None else [response_json]
            return [PkgbuildPatch.from_json(patch) for patch in patches]

        return []

    def package_patches_remove(self, package_base: str, variable: str | None) -> None:
        """
        remove package patch

        Args:
            package_base(str): package base to update
            variable(str | None): patch name. If ``None`` is set, all patches will be removed
        """
        with contextlib.suppress(Exception):
            self.make_request("DELETE", self._patches_url(package_base, variable or ""))

    def package_patches_update(self, package_base: str, patch: PkgbuildPatch) -> None:
        """
        create or update package patch

        Args:
            package_base(str): package base to update
            patch(PkgbuildPatch): package patch
        """
        with contextlib.suppress(Exception):
            self.make_request("POST", self._patches_url(package_base), json=patch.view())

    def package_remove(self, package_base: str) -> None:
        """
        remove packages from watcher

        Args:
            package_base(str): basename to remove
        """
        with contextlib.suppress(Exception):
            self.make_request("DELETE", self._package_url(package_base), params=self.repository_id.query())

    def package_status_update(self, package_base: str, status: BuildStatusEnum) -> None:
        """
        update package build status. Unlike :func:`package_update()` it does not update package properties

        Args:
            package_base(str): package base to update
            status(BuildStatusEnum): current package build status

        Raises:
            NotImplementedError: not implemented method
        """
        payload = {"status": status.value}

        with contextlib.suppress(Exception):
            self.make_request("POST", self._package_url(package_base),
                              params=self.repository_id.query(), json=payload)

    def package_update(self, package: Package, status: BuildStatusEnum) -> None:
        """
        add new package or update existing one with status

        Args:
            package(Package): package properties
            status(BuildStatusEnum): current package build status

        Raises:
            NotImplementedError: not implemented method
        """
        payload = {
            "status": status.value,
            "package": package.view(),
        }

        with contextlib.suppress(Exception):
            self.make_request("POST", self._package_url(package.base),
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
