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

from dataclasses import dataclass, field, fields
from pathlib import Path
from pyalpm import Package  # type: ignore
from typing import Any, Dict, List, Optional, Type

from ahriman.core.util import filter_json


@dataclass
class PackageDescription:
    """
    package specific properties
    :ivar architecture: package architecture
    :ivar archive_size: package archive size
    :ivar build_date: package build date
    :ivar depends: package dependencies list
    :ivar description: package description
    :ivar filename: package archive name
    :ivar groups: package groups
    :ivar installed_size: package installed size
    :ivar licenses: package licenses list
    :ivar provides: list of provided packages
    :ivar url: package url
    """

    architecture: Optional[str] = None
    archive_size: Optional[int] = None
    build_date: Optional[int] = None
    depends: List[str] = field(default_factory=list)
    description: Optional[str] = None
    filename: Optional[str] = None
    groups: List[str] = field(default_factory=list)
    installed_size: Optional[int] = None
    licenses: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)
    url: Optional[str] = None

    @property
    def filepath(self) -> Optional[Path]:
        """
        :return: path object for current filename
        """
        return Path(self.filename) if self.filename is not None else None

    @classmethod
    def from_json(cls: Type[PackageDescription], dump: Dict[str, Any]) -> PackageDescription:
        """
        construct package properties from json dump
        :param dump: json dump body
        :return: package properties
        """
        # filter to only known fields
        known_fields = [pair.name for pair in fields(cls)]
        return cls(**filter_json(dump, known_fields))

    @classmethod
    def from_package(cls: Type[PackageDescription], package: Package, path: Path) -> PackageDescription:
        """
        construct class from alpm package class
        :param package: alpm generated object
        :param path: path to package archive
        :return: package properties based on tarball
        """
        return cls(
            architecture=package.arch,
            archive_size=package.size,
            build_date=package.builddate,
            depends=package.depends,
            description=package.desc,
            filename=path.name,
            groups=package.groups,
            installed_size=package.isize,
            licenses=package.licenses,
            provides=package.provides,
            url=package.url)
