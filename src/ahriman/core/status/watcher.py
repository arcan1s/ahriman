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
import json
import logging

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import UnknownPackage
from ahriman.core.repository.repository import Repository
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.package import Package


class Watcher:
    """
    package status watcher
    :ivar architecture: repository architecture
    :ivar known: list of known packages. For the most cases `packages` should be used instead
    :ivar logger: class logger
    :ivar repository: repository object
    :ivar status: daemon status
    """

    def __init__(self, architecture: str, config: Configuration) -> None:
        """
        default constructor
        :param architecture: repository architecture
        :param config: configuration instance
        """
        self.logger = logging.getLogger("http")

        self.architecture = architecture
        self.repository = Repository(architecture, config)

        self.known: Dict[str, Tuple[Package, BuildStatus]] = {}
        self.status = BuildStatus()

    @property
    def cache_path(self) -> Path:
        """
        :return: path to dump with json cache
        """
        return self.repository.paths.root / "status_cache.json"

    @property
    def packages(self) -> List[Tuple[Package, BuildStatus]]:
        """
        :return: list of packages together with their statuses
        """
        return list(self.known.values())

    def _cache_load(self) -> None:
        """
        update current state from cache
        """
        def parse_single(properties: Dict[str, Any]) -> None:
            package = Package.from_json(properties["package"])
            status = BuildStatus.from_json(properties["status"])
            if package.base in self.known:
                self.known[package.base] = (package, status)

        if not self.cache_path.is_file():
            return
        with self.cache_path.open() as cache:
            try:
                dump = json.load(cache)
            except Exception:
                self.logger.exception("cannot parse json from file")
                dump = {}
        for item in dump.get("packages", []):
            try:
                parse_single(item)
            except Exception:
                self.logger.exception(f"cannot parse item f{item} to package")

    def _cache_save(self) -> None:
        """
        dump current cache to filesystem
        """
        dump = {
            "packages": [
                {
                    "package": package.view(),
                    "status": status.view()
                } for package, status in self.packages
            ]
        }
        try:
            with self.cache_path.open("w") as cache:
                json.dump(dump, cache)
        except Exception:
            self.logger.exception("cannot dump cache")

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
            current = self.known.get(package.base)
            if current is None:
                status = BuildStatus()
            else:
                _, status = current
            self.known[package.base] = (package, status)
        self._cache_load()

    def remove(self, base: str) -> None:
        """
        remove package base from known list if any
        :param base: package base
        """
        self.known.pop(base, None)
        self._cache_save()

    def update(self, base: str, status: BuildStatusEnum, package: Optional[Package]) -> None:
        """
        update package status and description
        :param base: package base to update
        :param status: new build status
        :param package: optional new package description. In case if not set current properties will be used
        """
        if package is None:
            try:
                package, _ = self.known[base]
            except KeyError:
                raise UnknownPackage(base)
        full_status = BuildStatus(status)
        self.known[base] = (package, full_status)
        self._cache_save()

    def update_self(self, status: BuildStatusEnum) -> None:
        """
        update service status
        :param status: new service status
        """
        self.status = BuildStatus(status)
