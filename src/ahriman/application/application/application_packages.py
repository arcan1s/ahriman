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
import requests
import shutil

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from ahriman.application.application.application_properties import ApplicationProperties
from ahriman.core.build_tools.sources import Sources
from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.utils import package_like
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.result import Result


class ApplicationPackages(ApplicationProperties):
    """
    package control class
    """

    def _add_archive(self, source: str, *_: Any) -> None:
        """
        add package from archive

        Args:
            source(str): path to package archive

        Raises:
            UnknownPackageError: if specified path doesn't exist
        """
        local_path = Path(source)
        if not local_path.is_file():
            raise UnknownPackageError(source)

        dst = self.repository.paths.packages / local_path.name
        shutil.copy(local_path, dst)

    def _add_aur(self, source: str, username: str | None) -> None:
        """
        add package from AUR

        Args:
            source(str): package base name
            username(str | None): optional override of username for build process
        """
        package = Package.from_aur(source, username)
        self.database.build_queue_insert(package)
        self.reporter.set_unknown(package)

    def _add_directory(self, source: str, *_: Any) -> None:
        """
        add packages from directory

        Args:
            source(str): path to local directory

        Raises:
            UnknownPackageError: if specified package is unknown or doesn't exist
        """
        local_dir = Path(source)
        if not local_dir.is_dir():
            raise UnknownPackageError(source)

        for full_path in filter(package_like, local_dir.iterdir()):
            self._add_archive(str(full_path))

    def _add_local(self, source: str, username: str | None) -> None:
        """
        add package from local PKGBUILDs

        Args:
            source(str): path to directory with local source files
            username(str | None): optional override of username for build process

        Raises:
            UnknownPackageError: if specified package is unknown or doesn't exist
        """
        if (source_dir := Path(source)).is_dir():
            package = Package.from_build(source_dir, self.architecture, username)
            cache_dir = self.repository.paths.cache_for(package.base)
            shutil.copytree(source_dir, cache_dir, dirs_exist_ok=True)  # copy package to store in caches
            Sources.init(cache_dir)  # we need to run init command in directory where we do have permissions
        elif (source_dir := self.repository.paths.cache_for(source)).is_dir():
            package = Package.from_build(source_dir, self.architecture, username)
        else:
            raise UnknownPackageError(source)

        self.database.build_queue_insert(package)

    def _add_remote(self, source: str, *_: Any) -> None:
        """
        add package from remote sources (e.g. HTTP)

        Args:
            source(str): remote URL of the package archive

        Raises:
            UnknownPackageError: if specified package is unknown or doesn't exist
        """
        # timeout=None to suppress pylint warns. Also suppress bandit warnings
        try:
            response = requests.get(source, stream=True, timeout=None)  # nosec
            response.raise_for_status()
        except Exception:
            raise UnknownPackageError(source)

        dst = self.repository.paths.packages / Path(source).name  # URL is path, is not it?
        with dst.open("wb") as local_file:
            for chunk in response.iter_content(chunk_size=1024):
                local_file.write(chunk)

    def _add_repository(self, source: str, username: str | None) -> None:
        """
        add package from official repository

        Args:
            source(str): package base name
            username(str | None): optional override of username for build process
        """
        package = Package.from_official(source, self.repository.pacman, username)
        self.database.build_queue_insert(package)
        self.reporter.set_unknown(package)

    def add(self, packages: Iterable[str], source: PackageSource, username: str | None = None) -> None:
        """
        add packages for the next build

        Args:
            packages(Iterable[str]): list of package bases to add
            source(PackageSource): package source to add
            username(str | None, optional): optional override of username for build process (Default value = None)
        """
        for package in packages:
            resolved_source = source.resolve(package, self.repository.paths)
            fn = getattr(self, f"_add_{resolved_source.value}")
            fn(package, username)

    def on_result(self, result: Result) -> None:
        """
        generate report and sync to remote server

        Args:
            result(Result): build result

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def remove(self, packages: Iterable[str]) -> Result:
        """
        remove packages from repository

        Args:
            packages(Iterable[str]): list of packages (either base or name) to remove

        Returns:
            Result: removal result
        """
        result = self.repository.process_remove(packages)
        self.on_result(result)
        return result
