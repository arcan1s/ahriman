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
import requests
import shutil

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Iterable, Set

from ahriman.application.application.application_properties import ApplicationProperties
from ahriman.core.build_tools.sources import Sources
from ahriman.core.util import package_like
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.result import Result


class ApplicationPackages(ApplicationProperties):
    """
    package control class
    """

    def _finalize(self, result: Result) -> None:
        """
        generate report and sync to remote server

        Args:
            result(Result): build result

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def _known_packages(self) -> Set[str]:
        """
        load packages from repository and pacman repositories

        Returns:
            Set[str]: list of known packages

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def _add_archive(self, source: str, *_: Any) -> None:
        """
        add package from archive

        Args:
            source(str): path to package archive
        """
        local_path = Path(source)
        dst = self.repository.paths.packages / local_path.name
        shutil.copy(local_path, dst)

    def _add_aur(self, source: str, known_packages: Set[str], without_dependencies: bool) -> None:
        """
        add package from AUR

        Args:
            source(str): package base name
            known_packages(Set[str]): list of packages which are known by the service
            without_dependencies(bool): if set, dependency check will be disabled
        """
        package = Package.from_aur(source, self.repository.pacman)

        self.database.build_queue_insert(package)
        self.database.remote_update(package)

        with TemporaryDirectory(ignore_cleanup_errors=True) as dir_name, \
                (local_dir := Path(dir_name)):  # pylint: disable=confusing-with-statement
            Sources.load(local_dir, package, self.database.patches_get(package.base), self.repository.paths)
            self._process_dependencies(local_dir, known_packages, without_dependencies)

    def _add_directory(self, source: str, *_: Any) -> None:
        """
        add packages from directory

        Args:
            source(str): path to local directory
        """
        local_dir = Path(source)
        for full_path in filter(package_like, local_dir.iterdir()):
            self._add_archive(str(full_path))

    def _add_local(self, source: str, known_packages: Set[str], without_dependencies: bool) -> None:
        """
        add package from local PKGBUILDs

        Args:
            source(str): path to directory with local source files
            known_packages(Set[str]): list of packages which are known by the service
            without_dependencies(bool): if set, dependency check will be disabled
        """
        source_dir = Path(source)
        package = Package.from_build(source_dir)
        cache_dir = self.repository.paths.cache_for(package.base)
        shutil.copytree(source_dir, cache_dir)  # copy package to store in caches
        Sources.init(cache_dir)  # we need to run init command in directory where we do have permissions

        self.database.build_queue_insert(package)

        self._process_dependencies(cache_dir, known_packages, without_dependencies)

    def _add_remote(self, source: str, *_: Any) -> None:
        """
        add package from remote sources (e.g. HTTP)

        Args:
            source(str): remote URL of the package archive
        """
        dst = self.repository.paths.packages / Path(source).name  # URL is path, is not it?
        response = requests.get(source, stream=True, timeout=None)  # timeout=None to suppress pylint warns
        response.raise_for_status()

        with dst.open("wb") as local_file:
            for chunk in response.iter_content(chunk_size=1024):
                local_file.write(chunk)

    def _add_repository(self, source: str, *_: Any) -> None:
        """
        add package from official repository

        Args:
            source(str): package base name
        """
        package = Package.from_official(source, self.repository.pacman)
        self.database.build_queue_insert(package)
        self.database.remote_update(package)
        # repository packages must not depend on unknown packages, thus we are not going to process dependencies

    def _process_dependencies(self, local_dir: Path, known_packages: Set[str], without_dependencies: bool) -> None:
        """
        process package dependencies

        Args:
            local_dir(Path): path to local package sources (i.e. cloned AUR repository)
            known_packages(Set[str]): list of packages which are known by the service
            without_dependencies(bool): if set, dependency check will be disabled
        """
        if without_dependencies:
            return

        dependencies = Package.dependencies(local_dir)
        self.add(dependencies.difference(known_packages), PackageSource.AUR, without_dependencies)

    def add(self, names: Iterable[str], source: PackageSource, without_dependencies: bool) -> None:
        """
        add packages for the next build

        Args:
            names(Iterable[str]): list of package bases to add
            source(PackageSource): package source to add
            without_dependencies(bool): if set, dependency check will be disabled
        """
        known_packages = self._known_packages()  # speedup dependencies processing

        for name in names:
            resolved_source = source.resolve(name)
            fn = getattr(self, f"_add_{resolved_source.value}")
            fn(name, known_packages, without_dependencies)

    def remove(self, names: Iterable[str]) -> None:
        """
        remove packages from repository

        Args:
            names(Iterable[str]): list of packages (either base or name) to remove
        """
        self.repository.process_remove(names)
        self._finalize(Result())
