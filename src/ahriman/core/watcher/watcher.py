#
# Copyright (c) 2021 Evgenii Alekseev.
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
from typing import Dict, List, Optional, Tuple

from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.package import Package


class Watcher:
    '''
    package status watcher
    :ivar architecture: repository architecture
    :ivar known: list of known packages. For the most cases `packages` should be used instead
    :ivar repository: repository object
    '''

    def __init__(self, architecture: str, config: Configuration) -> None:
        '''
        default constructor
        :param architecture: repository architecture
        :param config: configuration instance
        '''
        self.architecture = architecture
        self.repository = Repository(architecture, config)

        self.known: Dict[str, Tuple[Package, BuildStatus]] = {}

    @property
    def packages(self) -> List[Tuple[Package, BuildStatus]]:
        '''
        :return: list of packages together with their statuses
        '''
        return [pair for pair in self.known.values()]

    def load(self) -> None:
        '''
        load packages from local repository. In case if last status is known, it will use it
        '''
        for package in self.repository.packages():
            # get status of build or assign unknown
            current = self.known.get(package.base)
            if current is None:
                status = BuildStatus()
            else:
                _, status = current
            self.known[package.base] = (package, status)

    def remove(self, base: str) -> None:
        '''
        remove package base from known list if any
        :param base: package base
        '''
        self.known.pop(base, None)

    def update(self, base: str, status: BuildStatusEnum, package: Optional[Package]) -> None:
        '''
        update package status and description
        :param base: package base to update
        :param status: new build status
        :param package: optional new package description. In case if not set current properties will be used
        '''
        if package is None:
            package, _ = self.known[base]
        full_status = BuildStatus(status)
        self.known[base] = (package, full_status)
