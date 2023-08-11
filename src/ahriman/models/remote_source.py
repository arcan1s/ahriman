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
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Self

from ahriman.core.exceptions import InitializeError
from ahriman.core.util import dataclass_view, filter_json
from ahriman.models.package_source import PackageSource


@dataclass(frozen=True, kw_only=True)
class RemoteSource:
    """
    remote package source properties

    Attributes:
        branch(str | None): branch of the git repository
        git_url(str | None): url of the git repository
        path(str | None): path to directory with PKGBUILD inside the git repository
        source(PackageSource): package source pointer used by some parsers
        web_url(str | None): url of the package in the web interface
    """

    source: PackageSource
    git_url: str | None = None
    web_url: str | None = None
    path: str | None = None
    branch: str | None = None

    def __post_init__(self) -> None:
        """
        convert source to enum type
        """
        object.__setattr__(self, "source", PackageSource(self.source))

    @property
    def is_remote(self) -> bool:
        """
        check if source is remote

        Returns:
            bool: True in case if package is well-known remote source (e.g. AUR) and False otherwise
        """
        return self.source in (PackageSource.AUR, PackageSource.Repository)

    @property
    def pkgbuild_dir(self) -> Path | None:
        """
        get path to directory with package sources (PKGBUILD etc)

        Returns:
            Path | None: path to directory with package sources based on settings if available
        """
        return Path(self.path) if self.path is not None else None

    @classmethod
    def from_json(cls, dump: dict[str, Any]) -> Self:
        """
        construct remote source from the json dump (or database row)

        Args:
            dump(dict[str, Any]): json dump body

        Returns:
            Self: remote source
        """
        # filter to only known fields
        known_fields = [pair.name for pair in fields(cls)]
        return cls(**filter_json(dump, known_fields))

    def git_source(self) -> tuple[str, str]:
        """
        get git source if available

        Returns:
            tuple[str, str]: git url and branch

        Raises:
            InitializeError: in case if git url and/or branch are not set
        """
        if self.git_url is None or self.branch is None:
            raise InitializeError("Remote source is empty")
        return self.git_url, self.branch

    def view(self) -> dict[str, Any]:
        """
        generate json package remote view

        Returns:
            dict[str, Any]: json-friendly dictionary
        """
        return dataclass_view(self)
