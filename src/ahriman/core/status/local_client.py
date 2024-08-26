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
from ahriman.core.database import SQLite
from ahriman.core.status import Client
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.changes import Changes
from ahriman.models.dependencies import Dependencies
from ahriman.models.event import Event, EventType
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.repository_id import RepositoryId


class LocalClient(Client):
    """
    local database handler

    Attributes:
        database(SQLite): database instance
        repository_id(RepositoryId): repository unique identifier
    """

    def __init__(self, repository_id: RepositoryId, database: SQLite) -> None:
        """
        default constructor

        Args:
            repository_id(RepositoryId): repository unique identifier
            database(SQLite): database instance:
        """
        self.database = database
        self.repository_id = repository_id

    def event_add(self, event: Event) -> None:
        """
        create new event

        Args:
            event(Event): audit log event
        """
        self.database.event_insert(event, self.repository_id)

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
        """
        return self.database.event_get(event, object_id, limit, offset, self.repository_id)

    def package_changes_get(self, package_base: str) -> Changes:
        """
        get package changes

        Args:
            package_base(str): package base to retrieve

        Returns:
            Changes: package changes if available and empty object otherwise
        """
        return self.database.changes_get(package_base, self.repository_id)

    def package_changes_update(self, package_base: str, changes: Changes) -> None:
        """
        update package changes

        Args:
            package_base(str): package base to update
            changes(Changes): changes descriptor
        """
        self.database.changes_insert(package_base, changes, self.repository_id)

    def package_dependencies_get(self, package_base: str) -> Dependencies:
        """
        get package dependencies

        Args:
            package_base(str): package base to retrieve

        Returns:
            list[Dependencies]: package implicit dependencies if available
        """
        return self.database.dependencies_get(package_base, self.repository_id).get(package_base, Dependencies())

    def package_dependencies_update(self, package_base: str, dependencies: Dependencies) -> None:
        """
        update package dependencies

        Args:
            package_base(str): package base to update
            dependencies(Dependencies): dependencies descriptor
        """
        self.database.dependencies_insert(package_base, dependencies, self.repository_id)

    def package_get(self, package_base: str | None) -> list[tuple[Package, BuildStatus]]:
        """
        get package status

        Args:
            package_base(str | None): package base to get

        Returns:
            list[tuple[Package, BuildStatus]]: list of current package description and status if it has been found
        """
        packages = self.database.packages_get(self.repository_id)
        if package_base is None:
            return packages
        return [(package, status) for package, status in packages if package.base == package_base]

    def package_logs_add(self, log_record_id: LogRecordId, created: float, message: str) -> None:
        """
        post log record

        Args:
            log_record_id(LogRecordId): log record id
            created(float): log created timestamp
            message(str): log message
        """
        self.database.logs_insert(log_record_id, created, message, self.repository_id)

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
        return self.database.logs_get(package_base, limit, offset, self.repository_id)

    def package_logs_remove(self, package_base: str, version: str | None) -> None:
        """
        remove package logs

        Args:
            package_base(str): package base
            version(str | None): package version to remove logs. If ``None`` is set, all logs will be removed
        """
        self.database.logs_remove(package_base, version, self.repository_id)

    def package_patches_get(self, package_base: str, variable: str | None) -> list[PkgbuildPatch]:
        """
        get package patches

        Args:
            package_base(str): package base to retrieve
            variable(str | None): optional filter by patch variable

        Returns:
            list[PkgbuildPatch]: list of patches for the specified package
        """
        variables = [variable] if variable is not None else None
        return self.database.patches_list(package_base, variables).get(package_base, [])

    def package_patches_remove(self, package_base: str, variable: str | None) -> None:
        """
        remove package patch

        Args:
            package_base(str): package base to update
            variable(str | None): patch name. If ``None`` is set, all patches will be removed
        """
        variables = [variable] if variable is not None else None
        self.database.patches_remove(package_base, variables)

    def package_patches_update(self, package_base: str, patch: PkgbuildPatch) -> None:
        """
        create or update package patch

        Args:
            package_base(str): package base to update
            patch(PkgbuildPatch): package patch
        """
        self.database.patches_insert(package_base, [patch])

    def package_remove(self, package_base: str) -> None:
        """
        remove packages from watcher

        Args:
            package_base(str): package base to remove
        """
        self.database.package_clear(package_base)

    def package_status_update(self, package_base: str, status: BuildStatusEnum) -> None:
        """
        update package build status. Unlike :func:`package_update()` it does not update package properties

        Args:
            package_base(str): package base to update
            status(BuildStatusEnum): current package build status

        Raises:
            NotImplementedError: not implemented method
        """
        self.database.status_update(package_base, BuildStatus(status), self.repository_id)

    def package_update(self, package: Package, status: BuildStatusEnum) -> None:
        """
        add new package or update existing one with status

        Args:
            package(Package): package properties
            status(BuildStatusEnum): current package build status

        Raises:
            NotImplementedError: not implemented method
        """
        self.database.package_update(package, self.repository_id)
        self.database.status_update(package.base, BuildStatus(status), self.repository_id)
