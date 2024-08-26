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
# pylint: disable=too-many-public-methods
from __future__ import annotations

from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.changes import Changes
from ahriman.models.dependencies import Dependencies
from ahriman.models.event import Event, EventType
from ahriman.models.internal_status import InternalStatus
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.repository_id import RepositoryId


class Client:
    """
    base build status reporter client
    """

    @staticmethod
    def load(repository_id: RepositoryId, configuration: Configuration, database: SQLite | None = None, *,
             report: bool = True) -> Client:
        """
        load client from settings

        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            database(SQLite | None, optional): database instance (Default value = None)
            report(bool, optional): force enable or disable reporting (Default value = True)

        Returns:
            Client: client according to current settings
        """
        def make_local_client() -> Client:
            if database is None:
                return Client()

            from ahriman.core.status.local_client import LocalClient
            return LocalClient(repository_id, database)

        if not report:
            return make_local_client()
        if not configuration.getboolean("status", "enabled", fallback=True):  # global switch
            return make_local_client()

        # new-style section
        address = configuration.get("status", "address", fallback=None)
        # old-style section
        legacy_address = configuration.get("web", "address", fallback=None)
        host = configuration.get("web", "host", fallback=None)
        port = configuration.getint("web", "port", fallback=None)
        socket = configuration.get("web", "unix_socket", fallback=None)

        # basically we just check if there is something we can use for interaction with remote server
        if address or legacy_address or (host and port) or socket:
            from ahriman.core.status.web_client import WebClient
            return WebClient(repository_id, configuration)

        return make_local_client()

    def event_add(self, event: Event) -> None:
        """
        create new event

        Args:
            event(Event): audit log event

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def event_get(self, event: str | EventType | None, object_id: str | None,
                  limit: int = -1, offset: int = 0) -> list[Event]:
        """
        retrieve list of events

        Args:
            event(str | EventType | None): filter by event type
            object_id(str | None): filter by event object
            limit(int, optional): limit records to the specified count, -1 means unlimited (Default value = -1)
            offset(int, optional): records offset (Default value = 0)

        Returns:
            list[Event]: list of audit log events

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def package_changes_get(self, package_base: str) -> Changes:
        """
        get package changes

        Args:
            package_base(str): package base to retrieve

        Returns:
            Changes: package changes if available and empty object otherwise

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def package_changes_update(self, package_base: str, changes: Changes) -> None:
        """
        update package changes

        Args:
            package_base(str): package base to update
            changes(Changes): changes descriptor

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def package_dependencies_get(self, package_base: str) -> Dependencies:
        """
        get package dependencies

        Args:
            package_base(str): package base to retrieve

        Returns:
            list[Dependencies]: package implicit dependencies if available

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def package_dependencies_update(self, package_base: str, dependencies: Dependencies) -> None:
        """
        update package dependencies

        Args:
            package_base(str): package base to update
            dependencies(Dependencies): dependencies descriptor

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def package_get(self, package_base: str | None) -> list[tuple[Package, BuildStatus]]:
        """
        get package status

        Args:
            package_base(str | None): package base to get

        Returns:
            list[tuple[Package, BuildStatus]]: list of current package description and status if it has been found

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def package_logs_add(self, log_record_id: LogRecordId, created: float, message: str) -> None:
        """
        post log record

        Args:
            log_record_id(LogRecordId): log record id
            created(float): log created timestamp
            message(str): log message
        """
        # this method does not raise NotImplementedError because it is actively used as dummy client for http log

    def package_logs_get(self, package_base: str, limit: int = -1, offset: int = 0) -> list[tuple[float, str]]:
        """
        get package logs

        Args:
            package_base(str): package base
            limit(int, optional): limit records to the specified count, -1 means unlimited (Default value = -1)
            offset(int, optional): records offset (Default value = 0)

        Returns:
            list[tuple[float, str]]: package logs

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def package_logs_remove(self, package_base: str, version: str | None) -> None:
        """
        remove package logs

        Args:
            package_base(str): package base
            version(str | None): package version to remove logs. If None set, all logs will be removed

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def package_patches_get(self, package_base: str, variable: str | None) -> list[PkgbuildPatch]:
        """
        get package patches

        Args:
            package_base(str): package base to retrieve
            variable(str | None): optional filter by patch variable

        Returns:
            list[PkgbuildPatch]: list of patches for the specified package

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def package_patches_remove(self, package_base: str, variable: str | None) -> None:
        """
        remove package patch

        Args:
            package_base(str): package base to update
            variable(str | None): patch name. If None set, all patches will be removed

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def package_patches_update(self, package_base: str, patch: PkgbuildPatch) -> None:
        """
        create or update package patch

        Args:
            package_base(str): package base to update
            patch(PkgbuildPatch): package patch

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def package_remove(self, package_base: str) -> None:
        """
        remove packages from watcher

        Args:
            package_base(str): package base to remove

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def package_status_update(self, package_base: str, status: BuildStatusEnum) -> None:
        """
        update package build status. Unlike :func:`package_update()` it does not update package properties

        Args:
            package_base(str): package base to update
            status(BuildStatusEnum): current package build status

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def package_update(self, package: Package, status: BuildStatusEnum) -> None:
        """
        add new package or update existing one with status

        Args:
            package(Package): package properties
            status(BuildStatusEnum): current package build status

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def set_building(self, package_base: str) -> None:
        """
        set package status to building

        Args:
            package_base(str): package base to update
        """
        self.package_status_update(package_base, BuildStatusEnum.Building)

    def set_failed(self, package_base: str) -> None:
        """
        set package status to failed

        Args:
            package_base(str): package base to update
        """
        self.package_status_update(package_base, BuildStatusEnum.Failed)

    def set_pending(self, package_base: str) -> None:
        """
        set package status to pending

        Args:
            package_base(str): package base to update
        """
        self.package_status_update(package_base, BuildStatusEnum.Pending)

    def set_success(self, package: Package) -> None:
        """
        set package status to success

        Args:
            package(Package): current package properties
        """
        self.package_update(package, BuildStatusEnum.Success)

    def set_unknown(self, package: Package) -> None:
        """
        set package status to unknown. Unlike other methods, this method also checks if package is known,
        and - in case if it is - it silently skips update

        Args:
            package(Package): current package properties
        """
        if self.package_get(package.base):
            return  # skip update in case if package is already known
        self.package_update(package, BuildStatusEnum.Unknown)

    def status_get(self) -> InternalStatus:
        """
        get internal service status

        Returns:
            InternalStatus: current internal (web) service status
        """
        return InternalStatus(status=BuildStatus())

    def status_update(self, status: BuildStatusEnum) -> None:
        """
        update ahriman status itself

        Args:
            status(BuildStatusEnum): current ahriman status
        """
