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
from threading import Lock

from ahriman.core.database import SQLite
from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.log import LazyLogging
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.changes import Changes
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.repository_id import RepositoryId


class Watcher(LazyLogging):
    """
    package status watcher

    Attributes:
        database(SQLite): database instance
        repository_id(RepositoryId): repository unique identifier
        status(BuildStatus): daemon status
    """

    def __init__(self, repository_id: RepositoryId, database: SQLite) -> None:
        """
        default constructor

        Args:
            repository_id(RepositoryId): repository unique identifier
            database(SQLite): database instance
        """
        self.repository_id = repository_id
        self.database = database

        self._lock = Lock()
        self._known: dict[str, tuple[Package, BuildStatus]] = {}
        self.status = BuildStatus()

        # special variables for updating logs
        self._last_log_record_id = LogRecordId("", "")

    @property
    def packages(self) -> list[tuple[Package, BuildStatus]]:
        """
        get current known packages list

        Returns:
            list[tuple[Package, BuildStatus]]: list of packages together with their statuses
        """
        with self._lock:
            return list(self._known.values())

    def load(self) -> None:
        """
        load packages from local database
        """
        with self._lock:
            self._known = {
                package.base: (package, status)
                for package, status in self.database.packages_get(self.repository_id)
            }

    def logs_get(self, package_base: str, limit: int = -1, offset: int = 0) -> list[tuple[float, str]]:
        """
        extract logs for the package base

        Args:
            package_base(str): package base
            limit(int, optional): limit records to the specified count, -1 means unlimited (Default value = -1)
            offset(int, optional): records offset (Default value = 0)

        Returns:
            list[tuple[float, str]]: package logs
        """
        self.package_get(package_base)
        return self.database.logs_get(package_base, limit, offset, self.repository_id)

    def logs_remove(self, package_base: str, version: str | None) -> None:
        """
        remove package related logs

        Args:
            package_base(str): package base
            version(str): package versio
        """
        self.database.logs_remove(package_base, version, self.repository_id)

    def logs_update(self, log_record_id: LogRecordId, created: float, record: str) -> None:
        """
        make new log record into database

        Args:
            log_record_id(LogRecordId): log record id
            created(float): log created timestamp
            record(str): log record
        """
        if self._last_log_record_id != log_record_id:
            # there is new log record, so we remove old ones
            self.logs_remove(log_record_id.package_base, log_record_id.version)
        self._last_log_record_id = log_record_id
        self.database.logs_insert(log_record_id, created, record, self.repository_id)

    def package_changes_get(self, package_base: str) -> Changes:
        """
        retrieve package changes

        Args:
            package_base(str): package base

        Returns:
            Changes: package changes if available
        """
        self.package_get(package_base)
        return self.database.changes_get(package_base, self.repository_id)

    def package_get(self, package_base: str) -> tuple[Package, BuildStatus]:
        """
        get current package base build status

        Args:
            package_base(str): package base

        Returns:
            tuple[Package, BuildStatus]: package and its status

        Raises:
            UnknownPackageError: if no package found
        """
        try:
            with self._lock:
                return self._known[package_base]
        except KeyError:
            raise UnknownPackageError(package_base) from None

    def package_remove(self, package_base: str) -> None:
        """
        remove package base from known list if any

        Args:
            package_base(str): package base
        """
        with self._lock:
            self._known.pop(package_base, None)
        self.database.package_remove(package_base, self.repository_id)
        self.logs_remove(package_base, None)

    def package_update(self, package_base: str, status: BuildStatusEnum, package: Package | None) -> None:
        """
        update package status and description

        Args:
            package_base(str): package base to update
            status(BuildStatusEnum): new build status
            package(Package | None): optional package description. In case if not set current properties will be used
        """
        if package is None:
            package, _ = self.package_get(package_base)
        full_status = BuildStatus(status)
        with self._lock:
            self._known[package_base] = (package, full_status)
        self.database.package_update(package, full_status, self.repository_id)

    def patches_get(self, package_base: str, variable: str | None) -> list[PkgbuildPatch]:
        """
        get patches for the package

        Args:
            package_base(str): package base
            variable(str | None): patch variable name if any

        Returns:
            list[PkgbuildPatch]: list of patches which are stored for the package
        """
        self.package_get(package_base)
        variables = [variable] if variable is not None else None
        return self.database.patches_list(package_base, variables).get(package_base, [])

    def patches_remove(self, package_base: str, variable: str) -> None:
        """
        remove package patch

        Args:
            package_base(str): package base
            variable(str): patch variable name
        """
        self.database.patches_remove(package_base, [variable])

    def patches_update(self, package_base: str, patch: PkgbuildPatch) -> None:
        """
        update package patch

        Args:
            package_base(str): package base
            patch(PkgbuildPatch): package patch
        """
        self.database.patches_insert(package_base, [patch])

    def status_update(self, status: BuildStatusEnum) -> None:
        """
        update service status

        Args:
            status(BuildStatusEnum): new service status
        """
        self.status = BuildStatus(status)
