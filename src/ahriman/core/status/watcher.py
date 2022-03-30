#
# Copyright (c) 2021 ahriman team.
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
import logging

from typing import Dict, List, Optional, Tuple

from ahriman.core.configuration import Configuration
from ahriman.core.database.sqlite import SQLite
from ahriman.core.exceptions import UnknownPackage
from ahriman.core.repository import Repository
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.package import Package


class Watcher:
    """
    package status watcher
    :ivar architecture: repository architecture
    :ivar database: database instance
    :ivar known: list of known packages. For the most cases `packages` should be used instead
    :ivar logger: class logger
    :ivar repository: repository object
    :ivar status: daemon status
    """

    def __init__(self, architecture: str, configuration: Configuration, database: SQLite) -> None:
        """
        default constructor
        :param architecture: repository architecture
        :param configuration: configuration instance
        :param database: database instance
        """
        self.logger = logging.getLogger("http")

        self.architecture = architecture
        self.database = database
        self.repository = Repository(architecture, configuration, database, no_report=True, unsafe=False)

        self.known: Dict[str, Tuple[Package, BuildStatus]] = {}
        self.status = BuildStatus()

    @property
    def packages(self) -> List[Tuple[Package, BuildStatus]]:
        """
        :return: list of packages together with their statuses
        """
        return list(self.known.values())

    def get(self, base: str) -> Tuple[Package, BuildStatus]:
        """
        get current package base build status
        :return: package and its status
        """
        try:
            return self.known[base]
        except KeyError:
            raise UnknownPackage(base)

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
        :param package_base: package base
        """
        self.known.pop(package_base, None)
        self.database.package_remove(package_base)

    def update(self, package_base: str, status: BuildStatusEnum, package: Optional[Package]) -> None:
        """
        update package status and description
        :param package_base: package base to update
        :param status: new build status
        :param package: optional new package description. In case if not set current properties will be used
        """
        if package is None:
            try:
                package, _ = self.known[package_base]
            except KeyError:
                raise UnknownPackage(package_base)
        full_status = BuildStatus(status)
        self.known[package_base] = (package, full_status)
        self.database.package_update(package, full_status)

    def update_self(self, status: BuildStatusEnum) -> None:
        """
        update service status
        :param status: new service status
        """
        self.status = BuildStatus(status)
