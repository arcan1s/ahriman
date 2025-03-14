#
# Copyright (c) 2021-2025 ahriman team.
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

from enum import StrEnum
from pathlib import Path
from urllib.parse import urlparse

from ahriman.core.utils import package_like
from ahriman.models.repository_paths import RepositoryPaths


class PackageSource(StrEnum):
    """
    package source for addition enumeration

    Attributes:
        Auto(PackageSource): automatically determine type of the source
        Archive(PackageSource): source is a package archive
        AUR(PackageSource): source is an AUR package for which it should search
        Directory(PackageSource): source is a directory which contains packages
        Local(PackageSource): source is locally stored PKGBUILD
        Remote(PackageSource): source is remote (http, ftp etc...) link
        Repository(PackageSource): source is official repository

    Examples:
        In case if source is unknown the :func:`resolve()` and the source
        descriptor is available method must be used::

            >>> real_source = PackageSource.Auto.resolve("ahriman", configuration.repository_paths)

        the code above will ensure that the presudo-source :attr:`Auto`
        will not be processed later.
    """

    Auto = "auto"
    Archive = "archive"
    AUR = "aur"
    Directory = "directory"
    Local = "local"
    Remote = "remote"
    Repository = "repository"

    def resolve(self, source: str, paths: RepositoryPaths) -> PackageSource:
        """
        resolve auto into the correct type

        Args:
            source(str): source of the package
            paths(RepositoryPaths): repository paths instance

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
            if (maybe_path / "PKGBUILD").is_file() or paths.cache_for(source).is_dir():
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
