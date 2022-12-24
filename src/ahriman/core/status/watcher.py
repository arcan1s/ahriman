#
# Copyright (c) 2021-2022 ahriman team.
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
import os

from typing import Dict, List, Optional, Tuple

from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.log import LazyLogging
from ahriman.core.repository import Repository
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package


class Watcher(LazyLogging):
    """
    package status watcher

    Attributes:
        architecture(str): repository architecture
        database(SQLite): database instance
        known(Dict[str, Tuple[Package, BuildStatus]]): list of known packages. For the most cases ``packages`` should
            be used instead
        repository(Repository): repository object
        status(BuildStatus): daemon status
    """

    def __init__(self, architecture: str, configuration: Configuration, database: SQLite) -> None:
        """
        default constructor

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            database(SQLite): database instance
        """
        self.architecture = architecture
        self.database = database
        self.repository = Repository.load(architecture, configuration, database, report=False, unsafe=False)

        self.known: Dict[str, Tuple[Package, BuildStatus]] = {}
        self.status = BuildStatus()

        # special variables for updating logs
        self._last_log_record_id = LogRecordId("", os.getpid())

    @property
    def packages(self) -> List[Tuple[Package, BuildStatus]]:
        """
        get current known packages list

        Returns:
            List[Tuple[Package, BuildStatus]]: list of packages together with their statuses
        """
        return list(self.known.values())

    def get(self, package_base: str) -> Tuple[Package, BuildStatus]:
        """
        get current package base build status

        Args:
            package_base(str): package base

        Returns:
            Tuple[Package, BuildStatus]: package and its status

        Raises:
            UnknownPackage: if no package found
        """
        try:
            return self.known[package_base]
        except KeyError:
            raise UnknownPackageError(package_base)

    def get_logs(self, package_base: str) -> str:
        """
        extract logs for the package base

        Args:
            package_base(str): package base

        Returns:
            str: package logs
        """
        return self.database.logs_get(package_base)

    def load(self) -> None:
        """
        load packages from local repository. In case if last status is known, it will use it
        """
        for package in self.repository.packages():
            # get status of build or assign unknown
            if (current := self.known.get(package.base)) is not None:
                _, status = current
            else:
                status = BuildStatus()
            self.known[package.base] = (package, status)

        for package, status in self.database.packages_get():
            if package.base in self.known:
                self.known[package.base] = (package, status)

    def remove(self, package_base: str) -> None:
        """
        remove package base from known list if any

        Args:
            package_base(str): package base
        """
        self.known.pop(package_base, None)
        self.database.package_remove(package_base)
        self.remove_logs(package_base, None)

    def remove_logs(self, package_base: str, current_process_id: Optional[int]) -> None:
        """
        remove package related logs

        Args:
            package_base(str): package base
            current_process_id(int): current process id
        """
        self.database.logs_remove(package_base, current_process_id)

    def update(self, package_base: str, status: BuildStatusEnum, package: Optional[Package]) -> None:
        """
        update package status and description

        Args:
            package_base(str): package base to update
            status(BuildStatusEnum): new build status
            package(Optional[Package]): optional new package description. In case if not set current properties will be used

        Raises:
            UnknownPackage: if no package found
        """
        if package is None:
            try:
                package, _ = self.known[package_base]
            except KeyError:
                raise UnknownPackageError(package_base)
        full_status = BuildStatus(status)
        self.known[package_base] = (package, full_status)
        self.database.package_update(package, full_status)

    def update_logs(self, log_record_id: LogRecordId, created: float, record: str) -> None:
        """
        make new log record into database

        Args:
            log_record_id(LogRecordId): log record id
            created(float): log created record
            record(str): log record
        """
        if self._last_log_record_id != log_record_id:
            # there is new log record, so we remove old ones
            self.remove_logs(log_record_id.package_base, log_record_id.process_id)
        self._last_log_record_id = log_record_id
        self.database.logs_insert(log_record_id, created, record)

    def update_self(self, status: BuildStatusEnum) -> None:
        """
        update service status

        Args:
            status(BuildStatusEnum): new service status
        """
        self.status = BuildStatus(status)
