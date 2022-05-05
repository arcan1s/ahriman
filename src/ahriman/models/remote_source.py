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

from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any, Dict, Optional, Type

from ahriman.core.util import filter_json
from ahriman.models.package_source import PackageSource


@dataclass
class RemoteSource:
    """
    remote package source properties

    Attributes:
        branch(str): branch of the git repository
        git_url(str): url of the git repository
        path(str): path to directory with PKGBUILD inside the git repository
        source(PackageSource): package source pointer used by some parsers
        web_url(str): url of the package in the web interface
    """

    git_url: str
    web_url: str
    path: str
    branch: str
    source: PackageSource

    def __post_init__(self) -> None:
        """
        convert source to enum type
        """
        self.source = PackageSource(self.source)

    @property
    def pkgbuild_dir(self) -> Path:
        """
        get path to directory with package sources (PKGBUILD etc)

        Returns:
            Path: path to directory with package sources based on settings
        """
        return Path(self.path)

    @classmethod
    def from_json(cls: Type[RemoteSource], dump: Dict[str, Any]) -> Optional[RemoteSource]:
        """
        construct remote source from the json dump (or database row)

        Args:
            dump(Dict[str, Any]): json dump body

        Returns:
            Optional[RemoteSource]: remote source
        """
        # filter to only known fields
        known_fields = [pair.name for pair in fields(cls)]
        dump = filter_json(dump, known_fields)
        if dump:
            return cls(**dump)
        return None

    @classmethod
    def from_source(cls: Type[RemoteSource], source: PackageSource, package_base: str,
                    repository: str) -> Optional[RemoteSource]:
        """
        generate remote source from the package base

        Args:
            source(PackageSource): source of the package
            package_base(str): package base
            repository(str): repository name

        Returns:
            Optional[RemoteSource]: generated remote source if any, None otherwise
        """
        if source == PackageSource.AUR:
            from ahriman.core.alpm.remote.aur import AUR
            return RemoteSource(
                git_url=AUR.remote_git_url(package_base, repository),
                web_url=AUR.remote_web_url(package_base),
                path=".",
                branch="master",
                source=source,
            )
        if source == PackageSource.Repository:
            from ahriman.core.alpm.remote.official import Official
            return RemoteSource(
                git_url=Official.remote_git_url(package_base, repository),
                web_url=Official.remote_web_url(package_base),
                path="trunk",
                branch=f"packages/{package_base}",
                source=source,
            )
        return None

    def view(self) -> Dict[str, Any]:
        """
        generate json package remote view

        Returns:
            Dict[str, Any]: json-friendly dictionary
        """
        return asdict(self)
