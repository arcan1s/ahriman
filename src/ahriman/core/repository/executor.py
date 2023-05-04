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
import shutil

from collections.abc import Iterable
from pathlib import Path
from tempfile import TemporaryDirectory

from ahriman.core.build_tools.task import Task
from ahriman.core.repository.cleaner import Cleaner
from ahriman.core.util import safe_filename
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription
from ahriman.models.result import Result


class Executor(Cleaner):
    """
    trait for common repository update processes
    """

    def load_archives(self, packages: Iterable[Path]) -> list[Package]:
        """
        load packages from list of archives

        Args:
            packages(Iterable[Path]): paths to package archives

        Returns:
            list[Package]: list of read packages

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def packages(self) -> list[Package]:
        """
        generate list of repository packages

        Returns:
            list[Package]: list of packages properties

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def process_build(self, updates: Iterable[Package]) -> Result:
        """
        build packages

        Args:
            updates(Iterable[Package]): list of packages properties to build

        Returns:
            Result: build result
        """
        def build_single(package: Package, local_path: Path) -> None:
            self.reporter.set_building(package.base)
            task = Task(package, self.configuration, self.paths)
            task.init(local_path, self.database)
            built = task.build(local_path)
            for src in built:
                dst = self.paths.packages / src.name
                shutil.move(src, dst)

        result = Result()
        for single in updates:
            with self.in_package_context(single.base), TemporaryDirectory(ignore_cleanup_errors=True) as dir_name:
                try:
                    build_single(single, Path(dir_name))
                    result.add_success(single)
                except Exception:
                    self.reporter.set_failed(single.base)
                    result.add_failed(single)
                    self.logger.exception("%s (%s) build exception", single.base, self.architecture)

        return result

    def process_remove(self, packages: Iterable[str]) -> Path:
        """
        remove packages from list

        Args:
            packages(Iterable[str]): list of package names or bases to remove

        Returns:
            Path: path to repository database
        """
        def remove_base(package_base: str) -> None:
            try:
                self.paths.tree_clear(package_base)  # remove all internal files
                self.database.build_queue_clear(package_base)
                self.database.patches_remove(package_base, [])
                self.database.logs_remove(package_base, None)
                self.reporter.remove(package_base)  # we only update status page in case of base removal
            except Exception:
                self.logger.exception("could not remove base %s", package_base)

        def remove_package(package: str, fn: Path) -> None:
            try:
                self.repo.remove(package, fn)  # remove the package itself
            except Exception:
                self.logger.exception("could not remove %s", package)

        packages_to_remove: dict[str, Path] = {}
        bases_to_remove: list[str] = []

        # build package list based on user input
        requested = set(packages)
        for local in self.packages():
            if local.base in packages or all(package in requested for package in local.packages):
                packages_to_remove.update({
                    package: properties.filepath
                    for package, properties in local.packages.items()
                    if properties.filepath is not None
                })
                bases_to_remove.append(local.base)
            elif requested.intersection(local.packages.keys()):
                packages_to_remove.update({
                    package: properties.filepath
                    for package, properties in local.packages.items()
                    if package in requested and properties.filepath is not None
                })

        # check for packages which were requested to remove, but weren't found locally
        # it might happen for example, if there were no success build before
        for unknown in requested:
            if unknown in packages_to_remove or unknown in bases_to_remove:
                continue
            bases_to_remove.append(unknown)

        # remove packages from repository files
        for package, filename in packages_to_remove.items():
            remove_package(package, filename)

        # remove bases from registered
        for package in bases_to_remove:
            remove_base(package)

        return self.repo.repo_path

    def process_update(self, packages: Iterable[Path]) -> Result:
        """
        sign packages, add them to repository and update repository database

        Args:
            packages(Iterable[Path]): list of filenames to run

        Returns:
            Result: path to repository database
        """
        def rename(archive: PackageDescription, package_base: str) -> None:
            if archive.filename is None:
                self.logger.warning("received empty package name for base %s", package_base)
                return  # suppress type checking, it never can be none actually
            if (safe := safe_filename(archive.filename)) != archive.filename:
                shutil.move(self.paths.packages / archive.filename, self.paths.packages / safe)
                archive.filename = safe

        def update_single(name: str | None, package_base: str) -> None:
            if name is None:
                self.logger.warning("received empty package name for base %s", package_base)
                return  # suppress type checking, it never can be none actually
            # in theory, it might be NOT packages directory, but we suppose it is
            full_path = self.paths.packages / name
            files = self.sign.process_sign_package(full_path, package_base)
            for src in files:
                dst = self.paths.repository / safe_filename(src.name)
                shutil.move(src, dst)
            package_path = self.paths.repository / safe_filename(name)
            self.repo.add(package_path)

        current_packages = self.packages()
        removed_packages: list[str] = []  # list of packages which have been removed from the base
        updates = self.load_archives(packages)

        result = Result()
        for local in updates:
            with self.in_package_context(local.base):
                try:
                    for description in local.packages.values():
                        rename(description, local.base)
                        update_single(description.filename, local.base)
                    self.reporter.set_success(local)
                    result.add_success(local)

                    current_package_archives = {
                        package
                        for current in current_packages
                        if current.base == local.base
                        for package in current.packages
                    }
                    removed_packages.extend(current_package_archives.difference(local.packages))
                except Exception:
                    self.reporter.set_failed(local.base)
                    result.add_failed(local)
                    self.logger.exception("could not process %s", local.base)
        self.clear_packages()

        self.process_remove(removed_packages)

        return result
