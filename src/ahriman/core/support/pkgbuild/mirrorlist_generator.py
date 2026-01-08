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
from collections.abc import Callable
from pathlib import Path

from ahriman.core.configuration import Configuration
from ahriman.core.support.pkgbuild.pkgbuild_generator import PkgbuildGenerator
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.repository_id import RepositoryId


class MirrorlistGenerator(PkgbuildGenerator):
    """
    generator for mirrorlist PKGBUILD

    Attributes:
        path(Path): path to mirrorlist relative to /
        pkgbuild_license(list[str]): mirrorlist package license
        pkgbuild_pkgdesc(str): mirrorlist package description
        pkgbuild_pkgname(str): mirrorlist package name
        pkgbuild_url(str): mirrorlist package home page
        servers(list[str]): list of mirror servers
    """

    def __init__(self, repository_id: RepositoryId, configuration: Configuration, section: str) -> None:
        """
        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            section(str): settings section name
        """
        # configuration fields
        self.servers = configuration.getlist(section, "servers")
        self.path = configuration.getpath(
            section, "path", fallback=Path("/") / "etc" / "pacman.d" / f"{repository_id.name}-mirrorlist")
        self.path = self.path.relative_to("/")  # in pkgbuild we are always operating with relative to / path
        # pkgbuild description fields
        self.pkgbuild_pkgname = configuration.get(section, "package", fallback=f"{repository_id.name}-mirrorlist")
        self.pkgbuild_pkgdesc = configuration.get(
            section, "description", fallback=f"{repository_id.name} mirror list for use by pacman")
        self.pkgbuild_license = configuration.getlist(section, "license", fallback=["Unlicense"])
        self.pkgbuild_url = configuration.get(section, "homepage", fallback="")

    @property
    def license(self) -> list[str]:
        """
        package licenses list

        Returns:
            list[str]: package licenses as PKGBUILD property
        """
        return self.pkgbuild_license

    @property
    def pkgdesc(self) -> str:
        """
        package description

        Returns:
            str: package description as PKGBUILD property
        """
        return self.pkgbuild_pkgdesc

    @property
    def pkgname(self) -> str:
        """
        package name

        Returns:
            str: package name as PKGBUILD property
        """
        return self.pkgbuild_pkgname

    @property
    def url(self) -> str:
        """
        package upstream url

        Returns:
            str: package upstream url as PKGBUILD property
        """
        return self.pkgbuild_url

    def _generate_mirrorlist(self, source_path: Path) -> None:
        """
        generate mirrorlist file

        Args:
            source_path(Path): destination of the mirrorlist content
        """
        content = "".join([f"Server = {server}\n" for server in self.servers])
        source_path.write_text(content, encoding="utf8")

    def package(self) -> str:
        """
        package function generator

        Returns:
            str: package() function for PKGBUILD
        """
        return f"""{{
  install -Dm644 "{Path("$srcdir") / "mirrorlist"}" "{Path("$pkgdir") / self.path}"
}}"""

    def patches(self) -> list[PkgbuildPatch]:
        """
        list of additional PKGBUILD properties

        Returns:
            list[PkgbuildPatch]: list of patches which generate PKGBUILD content
        """
        return [
            PkgbuildPatch("backup", [str(self.path)]),
        ]

    def sources(self) -> dict[str, Callable[[Path], None]]:
        """
        return list of sources for the package

        Returns:
            dict[str, Callable[[Path], None]]: map of source identifier (e.g. filename) to its generator function
        """
        return {
            "mirrorlist": self._generate_mirrorlist,
        }
