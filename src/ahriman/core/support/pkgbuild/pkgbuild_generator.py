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
import hashlib
import itertools

from collections.abc import Callable, Generator
from pathlib import Path
from typing import ClassVar

from ahriman.core.utils import utcnow
from ahriman.models.pkgbuild_patch import PkgbuildPatch


class PkgbuildGenerator:
    """
    main class for generating PKGBUILDs

    Attributes:
        PKGBUILD_STATIC_PROPERTIES(list[PkgbuildPatch]): (class attribute) list of default pkgbuild static properties
    """

    PKGBUILD_STATIC_PROPERTIES: ClassVar[list[PkgbuildPatch]] = [
        PkgbuildPatch("pkgrel", "1"),
        PkgbuildPatch("arch", ["any"]),
    ]

    @property
    def license(self) -> list[str]:
        """
        package licenses list

        Returns:
            list[str]: package licenses as PKGBUILD property
        """
        return []

    @property
    def pkgdesc(self) -> str:
        """
        package description

        Returns:
            str: package description as PKGBUILD property

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    @property
    def pkgname(self) -> str:
        """
        package name

        Returns:
            str: package name as PKGBUILD property

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    @property
    def pkgver(self) -> str:
        """
        package version

        Returns:
            str: package version as PKGBUILD property
        """
        return utcnow().strftime("%Y%m%d")

    @property
    def url(self) -> str:
        """
        package upstream url

        Returns:
            str: package upstream url as PKGBUILD property
        """
        return ""

    def install(self) -> str | None:
        """
        content of the .install functions

        Returns:
            str | None: content of the .install functions if any
        """

    def package(self) -> str:
        """
        package function generator

        Returns:
            str: package() function for PKGBUILD

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def patches(self) -> list[PkgbuildPatch]:
        """
        list of additional PKGBUILD properties

        Returns:
            list[PkgbuildPatch]: list of patches which generate PKGBUILD content
        """
        return []

    def sources(self) -> dict[str, Callable[[Path], None]]:
        """
        return list of sources for the package

        Returns:
            dict[str, Callable[[Path], None]]: map of source identifier (e.g. filename) to its generator function
        """
        return {}

    def write_install(self, source_dir: Path) -> list[PkgbuildPatch]:
        """
        generate content of install file

        Args:
            source_dir(Path): path to directory in which sources must be generated

        Returns:
            list[PkgbuildPatch]: patch for the pkgbuild if install file exists and empty list otherwise
        """
        content: str | None = self.install()
        if content is None:
            return []

        source_path = source_dir / f"{self.pkgname}.install"
        source_path.write_text(content)
        return [PkgbuildPatch("install", source_path.name)]

    def write_pkgbuild(self, source_dir: Path) -> None:
        """
        generate PKGBUILD content to the specified path

        Args:
            source_dir(Path): path to directory in which sources must be generated
        """
        patches = self.PKGBUILD_STATIC_PROPERTIES  # default static properties...
        patches.extend([
            PkgbuildPatch("license", self.license),
            PkgbuildPatch("pkgdesc", self.pkgdesc),
            PkgbuildPatch("pkgname", self.pkgname),
            PkgbuildPatch("pkgver", self.pkgver),
            PkgbuildPatch("url", self.url),
        ])  # ...main properties as defined by derived class...
        patches.extend(self.patches())  # ...optional properties as defined by derived class...
        patches.extend(self.write_install(source_dir))  # ...install function...
        patches.append(PkgbuildPatch("package()", self.package()))  # ...package function...

        patches.extend(self.write_sources(source_dir))  # ...and finally source files

        for patch in patches:
            patch.write(source_dir / "PKGBUILD")

    def write_sources(self, source_dir: Path) -> list[PkgbuildPatch]:
        """
        write sources and returns valid PKGBUILD properties for them

        Args:
            source_dir(Path): path to directory in which sources must be generated

        Returns:
            list[PkgbuildPatch]: list of patches to be applied to the PKGBUILD
        """
        def sources_generator() -> Generator[tuple[str, str], None, None]:
            for source, generator in sorted(self.sources().items()):
                source_path = source_dir / source
                generator(source_path)
                with source_path.open("rb") as source_file:
                    source_hash = hashlib.sha512(source_file.read())
                yield source, source_hash.hexdigest()

        sources_iter, hashes_iter = itertools.tee(sources_generator())
        return [
            PkgbuildPatch("source", [source for source, _ in sources_iter]),
            PkgbuildPatch("sha512sums", [sha512 for _, sha512 in hashes_iter]),
        ]
