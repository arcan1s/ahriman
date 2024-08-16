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
import datetime
import inflection

from collections.abc import Callable
from dataclasses import dataclass, field, fields
from pyalpm import Package  # type: ignore[import-not-found]
from typing import Any, Self

from ahriman.core.utils import filter_json, full_version


@dataclass(frozen=True, kw_only=True)
class AURPackage:
    """
    AUR package descriptor

    Attributes:
        id(int): package ID
        name(str): package name
        package_base_id(int): package base ID
        version(str): package base version
        description(str): package base description
        url(str | None): package upstream URL
        num_votes(int): number of votes for the package
        popularity(float): package popularity
        out_of_date(datetime.datetime | None): package out of date timestamp if any
        maintainer(str | None): package maintainer
        submitter(str | None): package first submitter
        first_submitted(datetime.datetime): timestamp of the first package submission
        last_modified(datetime.datetime): timestamp of the last package submission
        url_path(str): AUR package path
        repository(str): repository name of the package
        depends(list[str]): list of package dependencies
        make_depends(l[str]): list of package make dependencies
        opt_depends(list[str]): list of package optional dependencies
        check_depends(list[str]): list of package test dependencies
        conflicts(list[str]): conflicts list for the package
        provides(list[str]): list of packages which this package provides
        license(list[str]): list of package licenses
        keywords(list[str]): list of package keywords
        groups(list[str]): list of package groups

    Examples:
        Mainly this class must be used from class methods instead of default :func:`__init__()`::

            >>> package = AURPackage.from_json(metadata)  # load package from json dump
            >>> # ...or alternatively...
            >>> package = AURPackage.from_repo(metadata)  # load package from official repository RPC
            >>> # properties of the class are built based on ones from AUR RPC, thus additional method is required
            >>>
            >>> from ahriman.core.alpm.pacman import Pacman
            >>> from ahriman.core.configuration import Configuration
            >>> from ahriman.models.repository_id import RepositoryId
            >>>
            >>> configuration = Configuration()
            >>> pacman = Pacman(RepositoryId("x86_64", "aur-clone"), configuration)
            >>> metadata = pacman.package_get("pacman")
            >>> package = AURPackage.from_pacman(next(metadata))  # load package from pyalpm wrapper
    """

    id: int
    name: str
    package_base_id: int
    package_base: str
    version: str
    num_votes: int
    popularity: float
    first_submitted: datetime.datetime
    last_modified: datetime.datetime
    url_path: str
    description: str = ""  # despite the fact that the field is required some packages don't have it
    url: str | None = None
    out_of_date: datetime.datetime | None = None
    maintainer: str | None = None
    submitter: str | None = None
    repository: str = "aur"
    depends: list[str] = field(default_factory=list)
    make_depends: list[str] = field(default_factory=list)
    opt_depends: list[str] = field(default_factory=list)
    check_depends: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    provides: list[str] = field(default_factory=list)
    license: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    groups: list[str] = field(default_factory=list)

    @classmethod
    def from_json(cls, dump: dict[str, Any]) -> Self:
        """
        construct package descriptor from RPC properties

        Args:
            dump(dict[str, Any]): json dump body

        Returns:
            Self: AUR package descriptor
        """
        # filter to only known fields
        known_fields = [pair.name for pair in fields(cls)]
        properties = cls.convert(dump)
        return cls(**filter_json(properties, known_fields))

    @classmethod
    def from_pacman(cls, package: Package) -> Self:
        """
        construct package descriptor from official repository wrapper

        Args:
            package(Package): pyalpm package descriptor

        Returns:
            Self: AUR package descriptor
        """
        return cls(
            id=0,
            name=package.name,
            package_base_id=0,
            package_base=package.base,
            version=package.version,
            description=package.desc,
            num_votes=0,
            popularity=0.0,
            first_submitted=datetime.datetime.fromtimestamp(0, datetime.UTC),
            last_modified=datetime.datetime.fromtimestamp(package.builddate, datetime.UTC),
            url_path="",
            url=package.url,
            out_of_date=None,
            maintainer=None,
            submitter=None,
            repository=package.db.name,
            depends=package.depends,
            make_depends=package.makedepends,
            opt_depends=package.optdepends,
            check_depends=package.checkdepends,
            conflicts=package.conflicts,
            provides=package.provides,
            license=package.licenses,
            keywords=[],
            groups=package.groups,
        )

    @classmethod
    def from_repo(cls, dump: dict[str, Any]) -> Self:
        """
        construct package descriptor from official repository RPC properties

        Args:
            dump(dict[str, Any]): json dump body

        Returns:
            Self: AUR package descriptor
        """
        return cls(
            id=0,
            name=dump["pkgname"],
            package_base_id=0,
            package_base=dump["pkgbase"],
            version=full_version(dump["epoch"], dump["pkgver"], dump["pkgrel"]),
            description=dump["pkgdesc"],
            num_votes=0,
            popularity=0.0,
            first_submitted=datetime.datetime.fromtimestamp(0, datetime.UTC),
            last_modified=datetime.datetime.fromisoformat(dump["last_update"]),
            url_path="",
            url=dump["url"],
            out_of_date=datetime.datetime.fromisoformat(dump["flag_date"]) if dump.get("flag_date") else None,
            maintainer=next(iter(dump["maintainers"]), None),
            submitter=None,
            repository=dump["repo"],
            depends=dump["depends"],
            make_depends=dump["makedepends"],
            opt_depends=dump["optdepends"],
            check_depends=dump["checkdepends"],
            conflicts=dump["conflicts"],
            provides=dump["provides"],
            license=dump["licenses"],
            keywords=[],
            groups=dump["groups"],
        )

    @staticmethod
    def convert(descriptor: dict[str, Any]) -> dict[str, Any]:
        """
        covert AUR RPC key names to package keys

        Args:
            descriptor(dict[str, Any]): RPC package descriptor

        Returns:
            dict[str, Any]: package descriptor with names converted to snake case
        """
        identity_mapper: Callable[[Any], Any] = lambda value: value
        value_mapper: dict[str, Callable[[Any], Any]] = {
            "out_of_date": lambda value: datetime.datetime.fromtimestamp(value, datetime.UTC) if value is not None else None,
            "first_submitted": lambda value: datetime.datetime.fromtimestamp(value, datetime.UTC),
            "last_modified": lambda value: datetime.datetime.fromtimestamp(value, datetime.UTC),
        }

        result: dict[str, Any] = {}
        for api_key, api_value in descriptor.items():
            property_key = inflection.underscore(api_key)
            mapper = value_mapper.get(property_key, identity_mapper)
            result[property_key] = mapper(api_value)

        return result
