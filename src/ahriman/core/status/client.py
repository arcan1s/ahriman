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
from __future__ import annotations

from typing import List, Optional, Tuple

from ahriman.core.configuration import Configuration
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.package import Package


class Client:
    """
    base build status reporter client
    """

    def add(self, package: Package, status: BuildStatusEnum) -> None:
        """
        add new package with status
        :param package: package properties
        :param status: current package build status
        """

    # pylint: disable=R0201
    def get(self, base: Optional[str]) -> List[Tuple[Package, BuildStatus]]:
        """
        get package status
        :param base: package base to get
        :return: list of current package description and status if it has been found
        """
        del base
        return []

    # pylint: disable=R0201
    def get_self(self) -> BuildStatus:
        """
        get ahriman status itself
        :return: current ahriman status
        """
        return BuildStatus()

    def remove(self, base: str) -> None:
        """
        remove packages from watcher
        :param base: package base to remove
        """

    def update(self, base: str, status: BuildStatusEnum) -> None:
        """
        update package build status. Unlike `add` it does not update package properties
        :param base: package base to update
        :param status: current package build status
        """

    def update_self(self, status: BuildStatusEnum) -> None:
        """
        update ahriman status itself
        :param status: current ahriman status
        """

    def set_building(self, base: str) -> None:
        """
        set package status to building
        :param base: package base to update
        """
        return self.update(base, BuildStatusEnum.Building)

    def set_failed(self, base: str) -> None:
        """
        set package status to failed
        :param base: package base to update
        """
        return self.update(base, BuildStatusEnum.Failed)

    def set_pending(self, base: str) -> None:
        """
        set package status to pending
        :param base: package base to update
        """
        return self.update(base, BuildStatusEnum.Pending)

    def set_success(self, package: Package) -> None:
        """
        set package status to success
        :param package: current package properties
        """
        return self.add(package, BuildStatusEnum.Success)

    def set_unknown(self, package: Package) -> None:
        """
        set package status to unknown
        :param package: current package properties
        """
        return self.add(package, BuildStatusEnum.Unknown)

    @staticmethod
    def load(architecture: str, config: Configuration) -> Client:
        """
        load client from settings
        :param architecture: repository architecture
        :param config: configuration instance
        :return: client according to current settings
        """
        section = config.get_section_name("web", architecture)
        host = config.get(section, "host", fallback=None)
        port = config.getint(section, "port", fallback=None)
        if host is None or port is None:
            return Client()

        from ahriman.core.status.web_client import WebClient
        return WebClient(host, port)
