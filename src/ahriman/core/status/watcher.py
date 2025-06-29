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
from collections.abc import Callable
from threading import Lock
from typing import Any, Self

from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.log import LazyLogging
from ahriman.core.status import Client
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.changes import Changes
from ahriman.models.dependencies import Dependencies
from ahriman.models.event import Event, EventType
from ahriman.models.log_record import LogRecord
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
        Args:
            client(Client): reporter instance
        """
        self.client = client

        self._lock = Lock()
        self._known: dict[str, tuple[Package, BuildStatus]] = {}
        self.status = BuildStatus()

    @property
    def packages(self) -> list[tuple[Package, BuildStatus]]:
        """
        get current known packages list

        Returns:
            list[tuple[Package, BuildStatus]]: list of packages together with their statuses
        """
        with self._lock:
            return list(self._known.values())

    event_add: Callable[[Event], None]

    event_get: Callable[[str | EventType | None, str | None, int | None, int | None, int, int], list[Event]]

    def load(self) -> None:
        """
        load packages from local database
        """
        with self._lock:
            self._known = {
                package.base: (package, status)
                for package, status in self.client.package_get(None)
            }

    logs_rotate: Callable[[int], None]

    package_changes_get: Callable[[str], Changes]

    package_changes_update: Callable[[str, Changes], None]

    package_dependencies_get: Callable[[str], Dependencies]

    package_dependencies_update: Callable[[str, Dependencies], None]

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

    package_logs_add: Callable[[LogRecord], None]

    package_logs_get: Callable[[str, str | None, str | None, int, int], list[LogRecord]]

    package_logs_remove: Callable[[str, str | None], None]

    package_patches_get: Callable[[str, str | None], list[PkgbuildPatch]]

    package_patches_remove: Callable[[str, str], None]

    package_patches_update: Callable[[str, PkgbuildPatch], None]

    def package_remove(self, package_base: str) -> None:
        """
        remove package base from known list if any

        Args:
            package_base(str): package base
        """
        with self._lock:
            self._known.pop(package_base, None)
        self.client.package_remove(package_base)

    def package_status_update(self, package_base: str, status: BuildStatusEnum) -> None:
        """
        update package status

        Args:
            package_base(str): package base to update
            status(BuildStatusEnum): new build status
        """
        package, _ = self.package_get(package_base)
        with self._lock:
            self._known[package_base] = (package, BuildStatus(status))
        self.client.package_status_update(package_base, status)

    def package_update(self, package: Package, status: BuildStatusEnum) -> None:
        """
        update package

        Args:
            package(Package): package description
            status(BuildStatusEnum): new build status
        """
        with self._lock:
            self._known[package.base] = (package, BuildStatus(status))
        self.client.package_update(package, status)

    def status_update(self, status: BuildStatusEnum) -> None:
        """
        update service status

        Args:
            status(BuildStatusEnum): new service status
        """
        self.status = BuildStatus(status)

    def __call__(self, package_base: str | None) -> Self:
        """
        extract client for future calls

        Args:
            package_base(str | None): package base to validate that package exists if applicable

        Returns:
            Self: instance of self to pass calls to the client
        """
        if package_base is not None:
            _ = self.package_get(package_base)
        return self

    def __getattr__(self, item: str) -> Any:
        """
        proxy methods for reporter client

        Args:
            item(str): property name

        Returns:
            Any: attribute by its name

        Raises:
            AttributeError: in case if no such attribute found
        """
        if (method := getattr(self.client, item, None)) is not None:
            return method
        raise AttributeError(f"'{self.__class__.__qualname__}' object has no attribute '{item}'")
