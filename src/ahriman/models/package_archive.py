#
# Copyright (c) 2021-2024 ahriman team.
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
from dataclasses import dataclass
from elftools.elf.dynamic import DynamicSection
from elftools.elf.elffile import ELFFile
from pathlib import Path
from typing import IO

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.remote import OfficialSyncdb
from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.utils import walk
from ahriman.models.dependencies import Dependencies
from ahriman.models.filesystem_package import FilesystemPackage
from ahriman.models.package import Package
from ahriman.models.scan_paths import ScanPaths


@dataclass
class PackageArchive:
    """
    helper for package archives

    Attributes:
        package(Package): package descriptor
        pacman(Pacman): alpm wrapper instance
        root(Path): path to root filesystem
        scan_paths(ScanPaths): scan paths holder
    """

    root: Path
    package: Package
    pacman: Pacman
    scan_paths: ScanPaths

    @staticmethod
    def dynamic_needed(binary_path: Path) -> list[str]:
        """
        extract dynamic libraries required by the specified file

        Args:
            binary_path(Path): path to library, file, etc

        Returns:
            list[str]: libraries which this file linked dynamically. Returns empty set in case if file is not
            a binary or no dynamic section has been found
        """
        with binary_path.open("rb") as binary_file:
            if not PackageArchive.is_elf(binary_file):
                return []

            elf_file = ELFFile(binary_file)  # type: ignore[no-untyped-call]
            dynamic_section = next(
                (section for section in elf_file.iter_sections()  # type: ignore[no-untyped-call]
                 if isinstance(section, DynamicSection)),
                None)
            if dynamic_section is None:
                return []

            return [
                tag.needed
                for tag in dynamic_section.iter_tags()  # type: ignore[no-untyped-call]
                if tag.entry.d_tag == "DT_NEEDED"
            ]

    @staticmethod
    def is_elf(content: IO[bytes]) -> bool:
        """
        check if the content is actually elf file

        Args:
            content(IO[bytes]): content of the file

        Returns:
            bool: ``True`` in case if file has elf header and ``False`` otherwise
        """
        expected = b"\x7fELF"
        length = len(expected)

        magic_bytes = content.read(length)
        content.seek(0)  # reset reading position

        return magic_bytes == expected

    def _load_pacman_package(self, path: Path) -> FilesystemPackage:
        """
        load pacman package model from path

        Args:
            path(Path): path to package files database

        Returns:
            FilesystemPackage: generated pacman package model with empty paths
        """
        package_name, *_ = path.parent.name.rsplit("-", 2)
        try:
            pacman_package = OfficialSyncdb.info(package_name, pacman=self.pacman)
            return FilesystemPackage(
                package_name=package_name,
                depends=set(pacman_package.depends),
                opt_depends=set(pacman_package.opt_depends),
            )
        except UnknownPackageError:
            return FilesystemPackage(package_name=package_name, depends=set(), opt_depends=set())

    def _raw_dependencies_packages(self) -> dict[Path, list[FilesystemPackage]]:
        """
        extract the initial list of packages which contain specific path this package depends on

        Returns:
            dict[Path, list[FilesystemPackage]]: map of path to packages containing this path
        """
        dependencies, roots = self.depends_on_paths()
        installed_packages = self.installed_packages()
        # build list of packages, which contains both the package itself and (possible) debug packages
        packages = list(self.package.packages) + [f"{package}-debug" for package in self.package.packages]

        # build initial map of file path -> packages containing this path
        # in fact, keys will contain all libraries the package linked to and all directories it contains
        dependencies_per_path: dict[Path, list[FilesystemPackage]] = {}
        for package_base, package in installed_packages.items():
            if package_base in packages:
                continue  # skip package itself

            required_by = [directory for directory in package.directories if directory in roots]
            required_by.extend(library for library in package.files if library.name in dependencies)

            for path in required_by:
                dependencies_per_path.setdefault(path, []).append(package)

        return dependencies_per_path

    def _refine_dependencies(self, source: dict[Path, list[FilesystemPackage]]) -> dict[Path, list[FilesystemPackage]]:
        """
        reduce the initial dependency list by removing packages which are already satisfied (e.g. by other path or by
        dependency list, or belonging to the base packages)

        Args:
            source(dict[Path, list[FilesystemPackage]]): the initial map of path to packages containing it

        Returns:
            dict[Path, list[FilesystemPackage]]: reduced source map of packages
        """
        # base packages should be always excluded from checking
        base_packages = OfficialSyncdb.info("base", pacman=self.pacman).depends

        result: dict[Path, list[FilesystemPackage]] = {}
        # sort items from children directories to root
        for path, packages in reversed(sorted(source.items())):
            # skip if this path belongs to the one of the base packages
            if any(package.package_name in base_packages for package in packages):
                continue

            # check path against the black/white listed
            if not self.scan_paths.is_allowed(path):
                continue

            # remove explicit dependencies
            packages = [package for package in packages if package.is_root_package(packages, include_optional=False)]
            # remove optional dependencies
            packages = [package for package in packages if package.is_root_package(packages, include_optional=True)]

            # check if there is already parent of current path in the result and has the same packages
            for children_path, children_packages in result.items():
                if not children_path.is_relative_to(path):
                    continue
                children_packages_names = {package.package_name for package in children_packages}
                packages = [package for package in packages if package.package_name not in children_packages_names]

            result[path] = packages

        return result

    def depends_on(self) -> Dependencies:
        """
        extract packages and paths which are required for this package

        Returns:
            Dependencies: map of the package name to set of paths used by this package
        """
        initial_packages = self._raw_dependencies_packages()
        refined_packages = self._refine_dependencies(initial_packages)

        paths = {
            str(path): [package.package_name for package in packages]
            for path, packages in refined_packages.items()
        }
        return Dependencies(paths)

    def depends_on_paths(self) -> tuple[set[str], set[Path]]:
        """
        extract dependencies from installation

        Returns:
            tuple[set[str], set[Path]]: tuple of dynamically linked libraries and directory paths
        """
        dependencies = set()
        roots: set[Path] = set()

        for package in self.package.packages:
            package_dir = self.root / "build" / self.package.base / "pkg" / package
            for path in filter(lambda p: p.is_file(), walk(package_dir)):
                dependencies.update(PackageArchive.dynamic_needed(path))
                filesystem_path = Path(*path.relative_to(package_dir).parts)
                roots.update(filesystem_path.parents[:-1])  # last element is always . because paths are relative

        return dependencies, roots

    def installed_packages(self) -> dict[str, FilesystemPackage]:
        """
        extract list of the installed packages and their content

        Returns:
            dict[str, FilesystemPackage]; map of package name to list of directories and files contained
            by this package
        """
        result = {}

        pacman_local_files = self.root / "var" / "lib" / "pacman" / "local"
        for path in filter(lambda fn: fn.name == "files", walk(pacman_local_files)):
            package = self._load_pacman_package(path)

            is_files_section = False
            for line in path.read_text(encoding="utf8").splitlines():
                if not line:  # skip empty lines
                    continue
                if line.startswith("%") and line.endswith("%"):  # directive started
                    is_files_section = line == "%FILES%"
                if not is_files_section:  # not a files directive
                    continue

                entry = Path(line)
                if line.endswith("/"):  # simple check if it is directory
                    package.directories.append(entry)
                else:
                    package.files.append(entry)

            result[package.package_name] = package

        return result
