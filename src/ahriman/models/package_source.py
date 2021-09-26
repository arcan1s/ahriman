#
# Copyright (c) 2021 ahriman team.
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

from ahriman.core.util import package_like


class PackageSource(Enum):
    """
    package source for addition enumeration
    :cvar Auto: automatically determine type of the source
    :cvar Archive: source is a package archive
    :cvar Directory: source is a directory which contains packages
    :cvar AUR: source is an AUR package for which it should search
    """

    Auto = "auto"
    Archive = "archive"
    Directory = "directory"
    AUR = "aur"

    def resolve(self, source: str) -> PackageSource:
        """
        resolve auto into the correct type
        :param source: source of the package
        :return: non-auto type of the package source
        """
        if self != PackageSource.Auto:
            return self
        maybe_path = Path(source)
        if maybe_path.is_dir():
            return PackageSource.Directory
        if maybe_path.is_file() and package_like(maybe_path):
            return PackageSource.Archive
        return PackageSource.AUR
