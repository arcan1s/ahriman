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
from typing import Any, Iterable, Set

from ahriman.application.application.properties import Properties
from ahriman.core.build_tools.sources import Sources
from ahriman.core.util import package_like, tmpdir
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.result import Result


class Packages(Properties):
    """
    package control class
    """

    def _finalize(self, result: Result) -> None:
        """
        generate report and sync to remote server
        :param result: build result
        """
        raise NotImplementedError

    def _known_packages(self) -> Set[str]:
        """
        load packages from repository and pacman repositories
        :return: list of known packages
        """
        raise NotImplementedError

    def _add_archive(self, source: str, *_: Any) -> None:
        """
        add package from archive
        :param source: path to package archive
        """
        local_path = Path(source)
        dst = self.repository.paths.packages / local_path.name
        shutil.copy(local_path, dst)

    def _add_aur(self, source: str, known_packages: Set[str], without_dependencies: bool) -> None:
        """
        add package from AUR
        :param source: package base name
        :param known_packages: list of packages which are known by the service
        :param without_dependencies: if set, dependency check will be disabled
        """
        package = Package.load(source, PackageSource.AUR, self.repository.pacman, self.repository.aur_url)

        self.database.build_queue_insert(package)

        with tmpdir() as local_path:
            Sources.load(local_path, package.git_url, self.database.patches_get(package.base))
            self._process_dependencies(local_path, known_packages, without_dependencies)

    def _add_directory(self, source: str, *_: Any) -> None:
        """
        add packages from directory
        :param source: path to local directory
        """
        local_path = Path(source)
        for full_path in filter(package_like, local_path.iterdir()):
            self._add_archive(str(full_path))

    def _add_local(self, source: str, known_packages: Set[str], without_dependencies: bool) -> None:
        """
        add package from local PKGBUILDs
        :param source: path to directory with local source files
        :param known_packages: list of packages which are known by the service
        :param without_dependencies: if set, dependency check will be disabled
        """
        package = Package.load(source, PackageSource.Local, self.repository.pacman, self.repository.aur_url)
        cache_dir = self.repository.paths.cache_for(package.base)
        shutil.copytree(Path(source), cache_dir)  # copy package to store in caches
        Sources.init(cache_dir)  # we need to run init command in directory where we do have permissions

        self.database.build_queue_insert(package)

        self._process_dependencies(cache_dir, known_packages, without_dependencies)

    def _add_remote(self, source: str, *_: Any) -> None:
        """
        add package from remote sources (e.g. HTTP)
        :param remote_url: remote URL to the package archive
        """
        dst = self.repository.paths.packages / Path(source).name  # URL is path, is not it?
        response = requests.get(source, stream=True)
        response.raise_for_status()

        with dst.open("wb") as local_file:
            for chunk in response.iter_content(chunk_size=1024):
                local_file.write(chunk)

    def _process_dependencies(self, local_path: Path, known_packages: Set[str], without_dependencies: bool) -> None:
        """
        process package dependencies
        :param local_path: path to local package sources (i.e. cloned AUR repository)
        :param known_packages: list of packages which are known by the service
        :param without_dependencies: if set, dependency check will be disabled
        """
        if without_dependencies:
            return

        dependencies = Package.dependencies(local_path)
        self.add(dependencies.difference(known_packages), PackageSource.AUR, without_dependencies)

    def add(self, names: Iterable[str], source: PackageSource, without_dependencies: bool) -> None:
        """
        add packages for the next build
        :param names: list of package bases to add
        :param source: package source to add
        :param without_dependencies: if set, dependency check will be disabled
        """
        known_packages = self._known_packages()  # speedup dependencies processing

        for name in names:
            resolved_source = source.resolve(name)
            fn = getattr(self, f"_add_{resolved_source.value}")
            fn(name, known_packages, without_dependencies)

    def remove(self, names: Iterable[str]) -> None:
        """
        remove packages from repository
        :param names: list of packages (either base or name) to remove
        """
        self.repository.process_remove(names)
        self._finalize(Result())
