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
from __future__ import annotations

import logging

from ahriman.core.configuration import Configuration
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.changes import Changes
from ahriman.models.internal_status import InternalStatus
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId


class Client:
    """
    base build status reporter client
    """

    @staticmethod
    def load(repository_id: RepositoryId, configuration: Configuration, *, report: bool) -> Client:
        """
        load client from settings

        Args:
            repository_id(RepositoryId): repository unqiue identifier
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting

        Returns:
            Client: client according to current settings
        """
        if not report:
            return Client()
        if not configuration.getboolean("status", "enabled", fallback=True):  # global switch
            return Client()

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
        return Client()

    def package_add(self, package: Package, status: BuildStatusEnum) -> None:
        """
        add new package with status

        Args:
            package(Package): package properties
            status(BuildStatusEnum): current package build status
        """

    def package_changes_get(self, package_base: str) -> Changes:
        """
        get package changes

        Args:
            package_base(str): package base to retrieve

        Returns:
            Changes: package changes if available and empty object otherwise
        """
        del package_base
        return Changes()

    def package_changes_set(self, package_base: str, changes: Changes) -> None:
        """
        update package changes

        Args:
            package_base(str): package base to update
            changes(Changes): changes descriptor
        """

    def package_get(self, package_base: str | None) -> list[tuple[Package, BuildStatus]]:
        """
        get package status

        Args:
            package_base(str | None): package base to get

        Returns:
            list[tuple[Package, BuildStatus]]: list of current package description and status if it has been found
        """
        del package_base
        return []

    def package_logs(self, log_record_id: LogRecordId, record: logging.LogRecord) -> None:
        """
        post log record

        Args:
            log_record_id(LogRecordId): log record id
            record(logging.LogRecord): log record to post to api
        """

    def package_remove(self, package_base: str) -> None:
        """
        remove packages from watcher

        Args:
            package_base(str): package base to remove
        """

    def package_update(self, package_base: str, status: BuildStatusEnum) -> None:
        """
        update package build status. Unlike :func:`package_add()` it does not update package properties

        Args:
            package_base(str): package base to update
            status(BuildStatusEnum): current package build status
        """

    def set_building(self, package_base: str) -> None:
        """
        set package status to building

        Args:
            package_base(str): package base to update
        """
        return self.package_update(package_base, BuildStatusEnum.Building)

    def set_failed(self, package_base: str) -> None:
        """
        set package status to failed

        Args:
            package_base(str): package base to update
        """
        return self.package_update(package_base, BuildStatusEnum.Failed)

    def set_pending(self, package_base: str) -> None:
        """
        set package status to pending

        Args:
            package_base(str): package base to update
        """
        return self.package_update(package_base, BuildStatusEnum.Pending)

    def set_success(self, package: Package) -> None:
        """
        set package status to success

        Args:
            package(Package): current package properties
        """
        return self.package_add(package, BuildStatusEnum.Success)

    def set_unknown(self, package: Package) -> None:
        """
        set package status to unknown

        Args:
            package(Package): current package properties
        """
        return self.package_add(package, BuildStatusEnum.Unknown)

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
