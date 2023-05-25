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
from collections.abc import Callable
from pathlib import Path

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import PkgbuildGeneratorError
from ahriman.core.sign.gpg import GPG
from ahriman.core.support.pkgbuild.pkgbuild_generator import PkgbuildGenerator


class KeyringGenerator(PkgbuildGenerator):
    """
    generator for keyring PKGBUILD

    Attributes:
        sign(GPG): GPG wrapper instance
        name(str): repository name
        packagers(list[str]): list of packagers PGP keys
        pkgbuild_license(list[str]): keyring package license
        pkgbuild_pkgdesc(str): keyring package description
        pkgbuild_pkgname(str): keyring package name
        pkgbuild_url(str): keyring package home page
        revoked(list[str]): list of revoked PGP keys
        trusted(list[str]): lif of trusted PGP keys
    """

    def __init__(self, sign: GPG, configuration: Configuration, section: str) -> None:
        """
        default constructor

        Args:
            sign(GPG): GPG wrapper instance
            configuration(Configuration): configuration instance
            section(str): settings section name
        """
        self.sign = sign
        self.name = configuration.repository_name

        # configuration fields
        self.packagers = configuration.getlist(section, "packagers", fallback=sign.keys())
        self.revoked = configuration.getlist(section, "revoked", fallback=[])
        self.trusted = configuration.getlist(
            section, "trusted", fallback=[sign.default_key] if sign.default_key is not None else [])
        # pkgbuild description fields
        self.pkgbuild_pkgname = configuration.get(section, "package", fallback=f"{self.name}-keyring")
        self.pkgbuild_pkgdesc = configuration.get(section, "description", fallback=f"{self.name} PGP keyring")
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

    def _generate_gpg(self, source_path: Path) -> None:
        """
        generate GPG keychain

        Args:
            source_path(Path): destination of the file content
        """
        with source_path.open("w") as source_file:
            for key in sorted(set(self.trusted + self.packagers + self.revoked)):
                public_key = self.sign.key_export(key)
                source_file.write(public_key)
                source_file.write("\n")

    def _generate_revoked(self, source_path: Path) -> None:
        """
        generate revoked PGP keys

        Args:
            source_path(Path): destination of the file content
        """
        with source_path.open("w") as source_file:
            for key in sorted(set(self.revoked)):
                fingerprint = self.sign.key_fingerprint(key)
                source_file.write(fingerprint)
                source_file.write("\n")

    def _generate_trusted(self, source_path: Path) -> None:
        """
        generate trusted PGP keys

        Args:
            source_path(Path): destination of the file content
        """
        if not self.trusted:
            raise PkgbuildGeneratorError
        with source_path.open("w") as source_file:
            for key in sorted(set(self.trusted)):
                fingerprint = self.sign.key_fingerprint(key)
                source_file.write(fingerprint)
                source_file.write(":4:\n")

    def install(self) -> str | None:
        """
        content of the install functions

        Returns:
            str | None: content of the install functions if any
        """
        # copy-paste from archlinux-keyring
        return f"""post_upgrade() {{
  if usr/bin/pacman-key -l >/dev/null 2>&1; then
    usr/bin/pacman-key --populate {self.name}
    usr/bin/pacman-key --updatedb
  fi
}}

post_install() {{
  if [ -x usr/bin/pacman-key ]; then
    post_upgrade
  fi
}}"""

    def package(self) -> str:
        """
        package function generator

        Returns:
            str: package() function for PKGBUILD
        """
        return f"""{{
  install -Dm644 "{Path("$srcdir") / f"{self.name}.gpg"}" "{Path("$pkgdir") / "usr" / "share" / "pacman" / "keyrings" / f"{self.name}.gpg"}"
  install -Dm644 "{Path("$srcdir") / f"{self.name}-revoked"}" "{Path("$pkgdir") / "usr" / "share" / "pacman" / "keyrings" / f"{self.name}-revoked"}"
  install -Dm644 "{Path("$srcdir") / f"{self.name}-trusted"}" "{Path("$pkgdir") / "usr" / "share" / "pacman" / "keyrings" / f"{self.name}-trusted"}"
}}"""

    def sources(self) -> dict[str, Callable[[Path], None]]:
        """
        return list of sources for the package

        Returns:
            dict[str, Callable[[Path], None]]: map of source identifier (e.g. filename) to its generator function
        """
        return {
            f"{self.name}.gpg": self._generate_gpg,
            f"{self.name}-revoked": self._generate_revoked,
            f"{self.name}-trusted": self._generate_trusted,
        }
