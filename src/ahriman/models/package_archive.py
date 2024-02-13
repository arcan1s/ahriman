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

from ahriman.core.util import walk
from ahriman.models.dependencies import Dependencies
from ahriman.models.package import Package


@dataclass
class PackageArchive:
    """
    helper for package archives

    Attributes:
        package(Package): package descriptor
        root(Path): path to root filesystem
    """

    root: Path
    package: Package

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
            bool: True in case if file has elf header and False otherwise
        """
        expected = b"\x7fELF"
        length = len(expected)

        magic_bytes = content.read(length)
        content.seek(0)  # reset reading position

        return magic_bytes == expected

    def depends_on(self) -> Dependencies:
        """
        extract packages and paths which are required for this package

        Returns:
            Dependencies: map of the package name to set of paths used by this package
        """
        dependencies, roots = self.depends_on_paths()

        result: dict[Path, list[str]] = {}
        for package, (directories, files) in self.installed_packages().items():
            if package in self.package.packages:
                continue  # skip package itself

            required_by = [directory for directory in directories if directory in roots]
            required_by.extend(library for library in files if library.name in dependencies)

            for path in required_by:
                result.setdefault(path, []).append(package)

        return Dependencies(self.package.base, result)

    def depends_on_paths(self) -> tuple[set[str], set[Path]]:
        """
        extract dependencies from installation

        Returns:
            tuple[set[str], set[Path]]: tuple of dynamically linked libraries and directory paths
        """
        dependencies = set()
        roots: set[Path] = set()

        package_dir = self.root / "build" / self.package.base / "pkg"
        for path in filter(lambda p: p.is_file(), walk(package_dir)):
            dependencies.update(PackageArchive.dynamic_needed(path))
            filesystem_path = Path(*path.relative_to(package_dir).parts[1:])
            roots.update(filesystem_path.parents[:-1])  # last element is always . because paths are relative

        return dependencies, roots

    def installed_packages(self) -> dict[str, tuple[list[Path], list[Path]]]:
        """
        extract list of the installed packages and their content

        Returns:
            dict[str, tuple[list[Path], list[Path]]]; map of package name to list of directories and files contained
            by this package
        """
        result = {}

        pacman_local_files = self.root / "var" / "lib" / "pacman" / "local"
        for path in filter(lambda fn: fn.name == "files", walk(pacman_local_files)):
            package, *_ = path.parent.name.rsplit("-", 2)

            directories, files = [], []
            is_files = False
            for line in path.read_text(encoding="utf8").splitlines():
                if not line:  # skip empty lines
                    continue
                if line.startswith("%") and line.endswith("%"):  # directive started
                    is_files = line == "%FILES%"
                if not is_files:  # not a files directive
                    continue

                entry = Path(line)
                if line.endswith("/"):  # simple check if it is directory
                    directories.append(entry)
                else:
                    files.append(entry)

            result[package] = directories, files

        return result
