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
from __future__ import annotations

from enum import Enum
from pathlib import Path
from urllib.parse import urlparse

from ahriman.core.util import package_like


class PackageSource(str, Enum):
    """
    package source for addition enumeration

    Attributes:
        Auto(PackageSource): (class attribute) automatically determine type of the source
        Archive(PackageSource): (class attribute) source is a package archive
        AUR(PackageSource): (class attribute) source is an AUR package for which it should search
        Directory(PackageSource): (class attribute) source is a directory which contains packages
        Local(PackageSource): (class attribute) source is locally stored PKGBUILD
        Remote(PackageSource): (class attribute) source is remote (http, ftp etc) link
        Repository(PackageSource): (class attribute) source is official repository

    Examples:
        In case if source is unknown the ``resolve()`` and the source descriptor is available method must be used::

            >>> real_source = PackageSource.Auto.resolve("ahriman")

        the code above will ensure that the presudo-source ``PackageSource.Auto`` will not be processed later.
    """

    Auto = "auto"
    Archive = "archive"
    AUR = "aur"
    Directory = "directory"
    Local = "local"
    Remote = "remote"
    Repository = "repository"

    def resolve(self, source: str) -> PackageSource:
        """
        resolve auto into the correct type

        Args:
            source(str): source of the package

        Returns:
            PackageSource: non-auto type of the package source
        """
        if self != PackageSource.Auto:
            return self

        maybe_url = urlparse(source)  # handle file:// like paths
        maybe_path = Path(maybe_url.path)

        if maybe_url.scheme and maybe_url.scheme not in ("data", "file") and package_like(maybe_path):
            return PackageSource.Remote
        try:
            if (maybe_path / "PKGBUILD").is_file():
                return PackageSource.Local
            if maybe_path.is_dir():
                return PackageSource.Directory
            if maybe_path.is_file() and package_like(maybe_path):
                return PackageSource.Archive
        except PermissionError:
            # in some cases (e.g. if you run from your home directory with sudo)
            # it will try to read files to which it has no access.
            # lets fallback to AUR source in these cases
            pass

        return PackageSource.AUR
