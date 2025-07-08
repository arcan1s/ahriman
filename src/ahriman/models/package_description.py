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
from dataclasses import dataclass, field, fields
from pathlib import Path
from pyalpm import Package  # type: ignore[import-not-found]
from typing import Any, Self

from ahriman.core.utils import dataclass_view, filter_json, trim_package
from ahriman.models.aur_package import AURPackage


@dataclass(kw_only=True)
class PackageDescription:
    """
    package specific properties

    Attributes:
        architecture(str | None): package architecture
        archive_size(int | None): package archive size
        build_date(int | None): package build date
        check_depends(list[str]): package dependencies list used for check functions
        depends(list[str]): package dependencies list
        opt_depends(list[str]): optional package dependencies list
        make_depends(list[str]): package dependencies list used for building
        description(str | None): package description
        filename(str | None): package archive name
        groups(list[str]): package groups
        installed_size(int | None): package installed size
        licenses(list[str]): package licenses list
        provides(list[str]): list of provided packages
        url(str | None): package url

    Examples:
        Unlike the :class:`ahriman.models.package.Package` class, this implementation only holds properties.
        The recommended way to deal with it is to read data based on the source type - either json or
        :class:`pyalpm.Package` instance::

            >>> description = PackageDescription.from_json(dump)
            >>>
            >>> from pathlib import Path
            >>> from ahriman.core.alpm.pacman import Pacman
            >>> from ahriman.core.configuration import Configuration
            >>> from ahriman.models.repository_id import RepositoryId
            >>>
            >>> configuration = Configuration()
            >>> pacman = Pacman(RepositoryId("x86_64", "aur"), configuration)
            >>> pyalpm_description = next(package for package in pacman.package_get("pacman"))
            >>> description = PackageDescription.from_package(
            >>>     pyalpm_description, Path("/var/cache/pacman/pkg/pacman-6.0.1-4-x86_64.pkg.tar.zst"))
    """

    architecture: str | None = None
    archive_size: int | None = None
    build_date: int | None = None
    depends: list[str] = field(default_factory=list)
    make_depends: list[str] = field(default_factory=list)
    opt_depends: list[str] = field(default_factory=list)
    check_depends: list[str] = field(default_factory=list)
    description: str | None = None
    filename: str | None = None
    groups: list[str] = field(default_factory=list)
    installed_size: int | None = None
    licenses: list[str] = field(default_factory=list)
    provides: list[str] = field(default_factory=list)
    url: str | None = None

    def __post_init__(self) -> None:
        """
        update packages lists accordingly
        """
        self.depends = [trim_package(package) for package in self.depends]
        self.make_depends = [trim_package(package) for package in self.make_depends]
        self.opt_depends = [trim_package(package) for package in self.opt_depends]
        self.check_depends = [trim_package(package) for package in self.check_depends]
        self.provides = [trim_package(package) for package in self.provides]

    @property
    def filepath(self) -> Path | None:
        """
        wrapper for filename, convert it to Path object

        Returns:
            Path | None: path object for current filename
        """
        return Path(self.filename) if self.filename is not None else None

    @classmethod
    def from_aur(cls, package: AURPackage) -> Self:
        """
        construct properties from AUR package model

        Args:
            package(AURPackage): AUR package model

        Returns:
            Self: package properties based on source AUR package
        """
        return cls(
            depends=package.depends,
            make_depends=package.make_depends,
            opt_depends=package.opt_depends,
            check_depends=package.check_depends,
            description=package.description,
            licenses=package.license,
            provides=package.provides,
            url=package.url,
        )

    @classmethod
    def from_json(cls, dump: dict[str, Any]) -> Self:
        """
        construct package properties from json dump

        Args:
            dump(dict[str, Any]): json dump body

        Returns:
            Self: package properties
        """
        # filter to only known fields
        known_fields = [pair.name for pair in fields(cls)]
        return cls(**filter_json(dump, known_fields))

    @classmethod
    def from_package(cls, package: Package, path: Path) -> Self:
        """
        construct class from alpm package class

        Args:
            package(Package): alpm generated object
            path(Path): path to package archive

        Returns:
            Self: package properties based on tarball
        """
        return cls(
            architecture=package.arch,
            archive_size=package.size,
            build_date=package.builddate,
            depends=package.depends,
            make_depends=package.makedepends,
            opt_depends=package.optdepends,
            check_depends=package.checkdepends,
            description=package.desc,
            filename=path.name,
            groups=package.groups,
            installed_size=package.isize,
            licenses=package.licenses,
            provides=package.provides,
            url=package.url,
        )

    def view(self) -> dict[str, Any]:
        """
        generate json package view

        Returns:
            dict[str, Any]: json-friendly dictionary
        """
        return dataclass_view(self)
