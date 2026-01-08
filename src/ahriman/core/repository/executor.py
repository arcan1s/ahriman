#
# Copyright (c) 2021-2026 ahriman team.
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

from ahriman.core.build_tools.package_archive import PackageArchive
from ahriman.core.build_tools.task import Task
from ahriman.core.repository.cleaner import Cleaner
from ahriman.core.repository.package_info import PackageInfo
from ahriman.core.utils import safe_filename
from ahriman.models.changes import Changes
from ahriman.models.event import EventType
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription
from ahriman.models.packagers import Packagers
from ahriman.models.result import Result


class Executor(PackageInfo, Cleaner):
    """
    trait for common repository update processes
    """

    def process_build(self, updates: Iterable[Package], packagers: Packagers | None = None, *,
                      bump_pkgrel: bool = False) -> Result:
        """
        build packages

        Args:
            updates(Iterable[Package]): list of packages properties to build
            packagers(Packagers | None, optional): optional override of username for build process
                (Default value = None)
            bump_pkgrel(bool, optional): bump pkgrel in case of local version conflict (Default value = False)

        Returns:
            Result: build result
        """
        def build_single(package: Package, local_path: Path, packager_id: str | None) -> str | None:
            self.reporter.set_building(package.base)
            task = Task(package, self.configuration, self.architecture, self.paths)
            local_version = local_versions.get(package.base) if bump_pkgrel else None
            patches = self.reporter.package_patches_get(package.base, None)
            commit_sha = task.init(local_path, patches, local_version)
            built = task.build(local_path, PACKAGER=packager_id)

            package.with_packages(built, self.pacman)
            for src in built:
                dst = self.paths.packages / src.name
                shutil.move(src, dst)

            return commit_sha

        packagers = packagers or Packagers()
        local_versions = {package.base: package.version for package in self.packages()}

        result = Result()
        for single in updates:
            with self.in_package_context(single.base, local_versions.get(single.base)), \
                    TemporaryDirectory(ignore_cleanup_errors=True) as dir_name:
                try:
                    with self.in_event(single.base, EventType.PackageUpdated, failure=EventType.PackageUpdateFailed):
                        packager = self.packager(packagers, single.base)
                        last_commit_sha = build_single(single, Path(dir_name), packager.packager_id)
                        # update commit hash for changes keeping current diff if there is any
                        changes = self.reporter.package_changes_get(single.base)
                        self.reporter.package_changes_update(single.base, Changes(last_commit_sha, changes.changes))
                        # update dependencies list
                        package_archive = PackageArchive(self.paths.build_root, single, self.pacman, self.scan_paths)
                        dependencies = package_archive.depends_on()
                        self.reporter.package_dependencies_update(single.base, dependencies)
                        # update result set
                        result.add_updated(single)
                except Exception:
                    self.reporter.set_failed(single.base)
                    result.add_failed(single)
                    self.logger.exception("%s (%s) build exception", single.base, self.architecture)

        return result

    def process_remove(self, packages: Iterable[str]) -> Result:
        """
        remove packages from list

        Args:
            packages(Iterable[str]): list of package names or bases to remove

        Returns:
            Result: remove result
        """
        def remove_base(package_base: str) -> None:
            try:
                with self.in_event(package_base, EventType.PackageRemoved):
                    self.reporter.package_remove(package_base)
            except Exception:
                self.logger.exception("could not remove base %s", package_base)

        def remove_package(package: str, archive_path: Path) -> None:
            try:
                self.repo.remove(package, archive_path)  # remove the package itself
            except Exception:
                self.logger.exception("could not remove %s", package)

        packages_to_remove: dict[str, Path] = {}
        bases_to_remove: list[str] = []

        # build package list based on user input
        result = Result()
        packages = set(packages)  # remove duplicates
        requested = packages | {f"{package}-debug" for package in packages}  # append debug packages
        for local in self.packages():
            if local.base in packages or all(package in requested for package in local.packages):
                packages_to_remove.update({
                    package: properties.filepath
                    for package, properties in local.packages.items()
                    if properties.filepath is not None
                })
                bases_to_remove.append(local.base)
                result.add_removed(local)
            elif requested.intersection(local.packages.keys()):
                packages_to_remove.update({
                    package: properties.filepath
                    for package, properties in local.packages.items()
                    if package in requested and properties.filepath is not None
                })

        # check for packages which were requested to remove, but weren't found locally
        # it might happen for example, if there were no success build before
        for unknown in packages:
            if unknown in packages_to_remove or unknown in bases_to_remove:
                continue
            bases_to_remove.append(unknown)

        # remove packages from repository files
        for package, filename in packages_to_remove.items():
            remove_package(package, filename)

        # remove bases from registered
        for package in bases_to_remove:
            remove_base(package)

        return result

    def process_update(self, packages: Iterable[Path], packagers: Packagers | None = None) -> Result:
        """
        sign packages, add them to repository and update repository database

        Args:
            packages(Iterable[Path]): list of filenames to run
            packagers(Packagers | None, optional): optional override of username for build process
                (Default value = None)

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

        def update_single(name: str | None, package_base: str, packager_key: str | None) -> None:
            if name is None:
                self.logger.warning("received empty package name for base %s", package_base)
                return  # suppress type checking, it never can be none actually
            # in theory, it might be NOT packages directory, but we suppose it is
            full_path = self.paths.packages / name
            files = self.sign.process_sign_package(full_path, packager_key)
            for src in files:
                dst = self.paths.repository / safe_filename(src.name)
                shutil.move(src, dst)
            package_path = self.paths.repository / safe_filename(name)
            self.repo.add(package_path)

        current_packages = {package.base: package for package in self.packages()}
        local_versions = {package_base: package.version for package_base, package in current_packages.items()}

        removed_packages: list[str] = []  # list of packages which have been removed from the base
        updates = self.load_archives(packages)
        packagers = packagers or Packagers()

        result = Result()
        for local in updates:
            with self.in_package_context(local.base, local_versions.get(local.base)):
                try:
                    packager = self.packager(packagers, local.base)

                    for description in local.packages.values():
                        rename(description, local.base)
                        update_single(description.filename, local.base, packager.key)
                    self.reporter.set_success(local)
                    result.add_updated(local)

                    current_package_archives: set[str] = set()
                    if local.base in current_packages:
                        current_package_archives = set(current_packages[local.base].packages.keys())
                    removed_packages.extend(current_package_archives.difference(local.packages))
                except Exception:
                    self.reporter.set_failed(local.base)
                    result.add_failed(local)
                    self.logger.exception("could not process %s", local.base)
        self.clear_packages()

        self.process_remove(removed_packages)

        return result
