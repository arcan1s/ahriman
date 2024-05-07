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
from threading import Lock

from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.log import LazyLogging
from ahriman.core.status import Client
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.changes import Changes
from ahriman.models.dependencies import Dependencies
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch


class Watcher(LazyLogging):
    """
    package status watcher

    Attributes:
        client(Client): reporter instance
        status(BuildStatus): daemon status
    """

    def __init__(self, client: Client) -> None:
        """
        default constructor

        Args:
            client(Client): reporter instance
        """
        self.client = client

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
                for package, status in self.client.package_get(None)
            }

    def package_add(self, package: Package, status: BuildStatusEnum) -> None:
        """
        update package

        Args:
            package(Package): package description
            status(BuildStatusEnum): new build status
        """
        with self._lock:
            self._known[package.base] = (package, BuildStatus(status))
        self.client.package_add(package, status)

    def package_changes_get(self, package_base: str) -> Changes:
        """
        retrieve package changes

        Args:
            package_base(str): package base

        Returns:
            Changes: package changes if available
        """
        _ = self.package_get(package_base)
        return self.client.package_changes_get(package_base)

    def package_changes_update(self, package_base: str, changes: Changes) -> None:
        """
        update package changes

        Args:
            package_base(str): package base
            changes(Changes): package changes
        """
        _ = self.package_get(package_base)
        self.client.package_changes_update(package_base, changes)

    def package_dependencies_get(self, package_base: str) -> Dependencies:
        """
        retrieve package dependencies

        Args:
            package_base(str): package base

        Returns:
            Dependencies: package dependencies if available
        """
        _ = self.package_get(package_base)
        return self.client.package_dependencies_get(package_base)

    def package_dependencies_update(self, package_base: str, dependencies: Dependencies) -> None:
        """
        update package dependencies

        Args:
            package_base(str): package base
            dependencies(Dependencies): package dependencies
        """
        _ = self.package_get(package_base)
        self.client.package_dependencies_update(package_base, dependencies)

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

    def package_logs_get(self, package_base: str, limit: int = -1, offset: int = 0) -> list[tuple[float, str]]:
        """
        extract logs for the package base

        Args:
            package_base(str): package base
            limit(int, optional): limit records to the specified count, -1 means unlimited (Default value = -1)
            offset(int, optional): records offset (Default value = 0)

        Returns:
            list[tuple[float, str]]: package logs
        """
        _ = self.package_get(package_base)
        return self.client.package_logs_get(package_base, limit, offset)

    def package_logs_remove(self, package_base: str, version: str | None) -> None:
        """
        remove package related logs

        Args:
            package_base(str): package base
            version(str): package version
        """
        self.client.package_logs_remove(package_base, version)

    def package_logs_update(self, log_record_id: LogRecordId, created: float, message: str) -> None:
        """
        make new log record into database

        Args:
            log_record_id(LogRecordId): log record id
            created(float): log created timestamp
            message(str): log message
        """
        if self._last_log_record_id != log_record_id:
            # there is new log record, so we remove old ones
            self.package_logs_remove(log_record_id.package_base, log_record_id.version)
        self._last_log_record_id = log_record_id
        self.client.package_logs_add(log_record_id, created, message)

    def package_patches_get(self, package_base: str, variable: str | None) -> list[PkgbuildPatch]:
        """
        get patches for the package

        Args:
            package_base(str): package base
            variable(str | None): patch variable name if any

        Returns:
            list[PkgbuildPatch]: list of patches which are stored for the package
        """
        # patches are package base based, we don't know (and don't differentiate) to which package does them belong
        # so here we skip checking if package exists or not
        return self.client.package_patches_get(package_base, variable)

    def package_patches_remove(self, package_base: str, variable: str) -> None:
        """
        remove package patch

        Args:
            package_base(str): package base
            variable(str): patch variable name
        """
        self.client.package_patches_remove(package_base, variable)

    def package_patches_update(self, package_base: str, patch: PkgbuildPatch) -> None:
        """
        update package patch

        Args:
            package_base(str): package base
            patch(PkgbuildPatch): package patch
        """
        self.client.package_patches_update(package_base, patch)

    def package_remove(self, package_base: str) -> None:
        """
        remove package base from known list if any

        Args:
            package_base(str): package base
        """
        with self._lock:
            self._known.pop(package_base, None)
        self.client.package_remove(package_base)
        self.package_logs_remove(package_base, None)

    def package_update(self, package_base: str, status: BuildStatusEnum) -> None:
        """
        update package status

        Args:
            package_base(str): package base to update
            status(BuildStatusEnum): new build status
        """
        package, _ = self.package_get(package_base)
        with self._lock:
            self._known[package_base] = (package, BuildStatus(status))
        self.client.package_update(package_base, status)

    def status_update(self, status: BuildStatusEnum) -> None:
        """
        update service status

        Args:
            status(BuildStatusEnum): new service status
        """
        self.status = BuildStatus(status)
