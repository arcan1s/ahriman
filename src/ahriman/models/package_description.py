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
from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from pyalpm import Package  # type: ignore
from typing import Any, Dict, List, Optional, Type

from ahriman.core.util import filter_json, trim_package
from ahriman.models.aur_package import AURPackage


@dataclass(kw_only=True)
class PackageDescription:
    """
    package specific properties

    Attributes:
        architecture(Optional[str]): package architecture
        archive_size(Optional[int]): package archive size
        build_date(Optional[int]): package build date
        depends(List[str]): package dependencies list
        opt_depends(List[str]): optional package dependencies list
        make_depends(List[str]): package dependencies list used for building
        description(Optional[str]): package description
        filename(Optional[str]): package archive name
        groups(List[str]): package groups
        installed_size(Optional[int]): package installed size
        licenses(List[str]): package licenses list
        provides(List[str]): list of provided packages
        url(Optional[str]): package url

    Examples:
        Unlike the ``Package`` class, this implementation only holds properties. The recommended way to deal with it is
        to read data based on the source type - either json or ``pyalpm.Package`` instance::

            >>> description = PackageDescription.from_json(dump)
            >>>
            >>>
            >>> from pathlib import Path
            >>> from ahriman.core.alpm.pacman import Pacman
            >>> from ahriman.core.configuration import Configuration
            >>>
            >>> configuration = Configuration()
            >>> pacman = Pacman("x86_64", configuration)
            >>> pyalpm_description = next(package for package in pacman.get("pacman"))
            >>> description = PackageDescription.from_package(
            >>>     pyalpm_description, Path("/var/cache/pacman/pkg/pacman-6.0.1-4-x86_64.pkg.tar.zst"))
    """

    architecture: Optional[str] = None
    archive_size: Optional[int] = None
    build_date: Optional[int] = None
    depends: List[str] = field(default_factory=list)
    make_depends: List[str] = field(default_factory=list)
    opt_depends: List[str] = field(default_factory=list)
    description: Optional[str] = None
    filename: Optional[str] = None
    groups: List[str] = field(default_factory=list)
    installed_size: Optional[int] = None
    licenses: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)
    url: Optional[str] = None

    def __post_init__(self) -> None:
        """
        update dependencies list accordingly
        """
        self.depends = [trim_package(package) for package in self.depends]
        self.opt_depends = [trim_package(package) for package in self.opt_depends]
        self.make_depends = [trim_package(package) for package in self.make_depends]

    @property
    def filepath(self) -> Optional[Path]:
        """
        wrapper for filename, convert it to Path object

        Returns:
            Optional[Path]: path object for current filename
        """
        return Path(self.filename) if self.filename is not None else None

    @classmethod
    def from_aur(cls: Type[PackageDescription], package: AURPackage) -> PackageDescription:
        """
        construct properties from AUR package model

        Args:
            package(AURPackage): AUR package model

        Returns:
            PackageDescription: package properties based on source AUR package
        """
        return cls(
            depends=package.depends,
            make_depends=package.make_depends,
            opt_depends=package.opt_depends,
            description=package.description,
            licenses=package.license,
            provides=package.provides,
            url=package.url,
        )

    @classmethod
    def from_json(cls: Type[PackageDescription], dump: Dict[str, Any]) -> PackageDescription:
        """
        construct package properties from json dump

        Args:
            dump(Dict[str, Any]): json dump body

        Returns:
            PackageDescription: package properties
        """
        # filter to only known fields
        known_fields = [pair.name for pair in fields(cls)]
        return cls(**filter_json(dump, known_fields))

    @classmethod
    def from_package(cls: Type[PackageDescription], package: Package, path: Path) -> PackageDescription:
        """
        construct class from alpm package class

        Args:
            package(Package): alpm generated object
            path(Path): path to package archive

        Returns:
            PackageDescription: package properties based on tarball
        """
        return cls(
            architecture=package.arch,
            archive_size=package.size,
            build_date=package.builddate,
            depends=package.depends,
            make_depends=package.makedepends,
            opt_depends=package.optdepends,
            description=package.desc,
            filename=path.name,
            groups=package.groups,
            installed_size=package.isize,
            licenses=package.licenses,
            provides=package.provides,
            url=package.url,
        )

    def view(self) -> Dict[str, Any]:
        """
        generate json package view

        Returns:
            Dict[str, Any]: json-friendly dictionary
        """
        return asdict(self)
