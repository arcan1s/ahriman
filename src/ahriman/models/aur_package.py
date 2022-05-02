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

import datetime
import inflection

from dataclasses import dataclass, field, fields
from pyalpm import Package  # type: ignore
from typing import Any, Callable, Dict, List, Optional, Type

from ahriman.core.util import filter_json, full_version


@dataclass
class AURPackage:
    """
    AUR package descriptor

    Attributes:
        id(int): package ID
        name(str): package name
        package_base_id(int): package base ID
        version(str): package base version
        description(str): package base description
        url(Optional[str]): package upstream URL
        num_votes(int): number of votes for the package
        polularity(float): package popularity
        out_of_date(Optional[datetime.datetime]): package out of date timestamp if any
        maintainer(Optional[str]): package maintainer
        first_submitted(datetime.datetime): timestamp of the first package submission
        last_modified(datetime.datetime): timestamp of the last package submission
        url_path(str): AUR package path
        repository(str): repository name of the package
        depends(List[str]): list of package dependencies
        make_depends(List[str]): list of package make dependencies
        opt_depends(List[str]): list of package optional dependencies
        conflicts(List[str]): conflicts list for the package
        provides(List[str]): list of packages which this package provides
        license(List[str]): list of package licenses
        keywords(List[str]): list of package keywords
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
    url: Optional[str] = None
    out_of_date: Optional[datetime.datetime] = None
    maintainer: Optional[str] = None
    repository: str = "aur"
    depends: List[str] = field(default_factory=list)
    make_depends: List[str] = field(default_factory=list)
    opt_depends: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)
    license: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

    @classmethod
    def from_json(cls: Type[AURPackage], dump: Dict[str, Any]) -> AURPackage:
        """
        construct package descriptor from RPC properties

        Args:
            dump(Dict[str, Any]): json dump body

        Returns:
            AURPackage: AUR package descriptor
        """
        # filter to only known fields
        known_fields = [pair.name for pair in fields(cls)]
        properties = cls.convert(dump)
        return cls(**filter_json(properties, known_fields))

    @classmethod
    def from_pacman(cls: Type[AURPackage], package: Package) -> AURPackage:
        """
        construct package descriptor from official repository wrapper

        Args:
            package(Package): pyalpm package descriptor

        Returns:
            AURPackage: AUR package descriptor
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
            first_submitted=datetime.datetime.utcfromtimestamp(0),
            last_modified=datetime.datetime.utcfromtimestamp(package.builddate),
            url_path="",
            url=package.url,
            out_of_date=None,
            maintainer=None,
            repository=package.db.name,
            depends=package.depends,
            make_depends=package.makedepends,
            opt_depends=package.optdepends,
            conflicts=package.conflicts,
            provides=package.provides,
            license=package.licenses,
            keywords=[],
        )

    @classmethod
    def from_repo(cls: Type[AURPackage], dump: Dict[str, Any]) -> AURPackage:
        """
        construct package descriptor from official repository RPC properties

        Args:
            dump(Dict[str, Any]): json dump body

        Returns:
            AURPackage: AUR package descriptor
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
            first_submitted=datetime.datetime.utcfromtimestamp(0),
            last_modified=datetime.datetime.strptime(dump["last_update"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            url_path="",
            url=dump["url"],
            out_of_date=datetime.datetime.strptime(
                dump["flag_date"],
                "%Y-%m-%dT%H:%M:%S.%fZ") if dump["flag_date"] is not None else None,
            maintainer=next(iter(dump["maintainers"]), None),
            repository=dump["repo"],
            depends=dump["depends"],
            make_depends=dump["makedepends"],
            opt_depends=dump["optdepends"],
            conflicts=dump["conflicts"],
            provides=dump["provides"],
            license=dump["licenses"],
            keywords=[],
        )

    @staticmethod
    def convert(descriptor: Dict[str, Any]) -> Dict[str, Any]:
        """
        covert AUR RPC key names to package keys

        Args:
            descriptor(Dict[str, Any]): RPC package descriptor

        Returns:
            Dict[str, Any]: package descriptor with names converted to snake case
        """
        identity_mapper: Callable[[Any], Any] = lambda value: value
        value_mapper: Dict[str, Callable[[Any], Any]] = {
            "out_of_date": lambda value: datetime.datetime.utcfromtimestamp(value) if value is not None else None,
            "first_submitted": datetime.datetime.utcfromtimestamp,
            "last_modified": datetime.datetime.utcfromtimestamp,
        }

        result: Dict[str, Any] = {}
        for api_key, api_value in descriptor.items():
            property_key = inflection.underscore(api_key)
            mapper = value_mapper.get(property_key, identity_mapper)
            result[property_key] = mapper(api_value)

        return result
