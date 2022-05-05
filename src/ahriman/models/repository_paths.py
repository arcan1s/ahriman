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

import os
import shutil

from dataclasses import dataclass
from pathlib import Path
from typing import Set, Tuple, Type

from ahriman.core.exceptions import InvalidPath


@dataclass
class RepositoryPaths:
    """
    repository paths holder. For the most operations with paths you want to use this object

    Attributes:
        root(Path): repository root (i.e. ahriman home)
        architecture(str): repository architecture

    Examples:
        This class can be used in order to access the repository tree structure::

            >>> paths = RepositoryPaths(Path("/var/lib/ahriman"), "x86_64")

        Additional methods can be used in order to ensure that tree is created::

            >>> paths.tree_create()

        Access to directories inside can be done by either using properties or specifying the package base::

            >>> cache_dir = paths.cache
            >>> ahriman_cache_dir = paths.cache_for("ahriman")
    """

    root: Path
    architecture: str

    @property
    def cache(self) -> Path:
        """
        get directory for packages cache (mainly used for VCS packages)

        Returns:
            Path: full path to cache directory
        """
        return self.root / "cache"

    @property
    def chroot(self) -> Path:
        """
        get directory for devtools chroot

        Returns:
            Path: full patch to devtools chroot directory
        """
        # for the chroot directory devtools will create own tree, and we don"t have to specify architecture here
        return self.root / "chroot"

    @property
    def packages(self) -> Path:
        """
        get directory for built packages

        Returns:
            Path: full path to built packages directory
        """
        return self.root / "packages" / self.architecture

    @property
    def repository(self) -> Path:
        """
        get repository directory

        Returns:
            Path: full path to the repository directory
        """
        return self.root / "repository" / self.architecture

    @property
    def root_owner(self) -> Tuple[int, int]:
        """
        get UID and GID of the root directory

        Returns:
            Tuple[int, int]: owner user and group of the root directory
        """
        return self.owner(self.root)

    @classmethod
    def known_architectures(cls: Type[RepositoryPaths], root: Path) -> Set[str]:
        """
        get known architectures

        Args:
            root(Path): repository root

        Returns:
            Set[str]: list of architectures for which tree is created
        """
        paths = cls(root, "")
        return {
            path.name
            for path in paths.repository.iterdir()
            if path.is_dir()
        }

    @staticmethod
    def owner(path: Path) -> Tuple[int, int]:
        """
        retrieve owner information by path

        Args:
            path(Path): path for which extract ids

        Returns:
            Tuple[int, int]: owner user and group ids of the directory
        """
        stat = path.stat()
        return stat.st_uid, stat.st_gid

    def cache_for(self, package_base: str) -> Path:
        """
        get path to cached PKGBUILD and package sources for the package base

        Args:
            package_base(str): package base name

        Returns:
            Path: full path to directory for specified package base cache
        """
        return self.cache / package_base

    def chown(self, path: Path) -> None:
        """
        set owner of path recursively (from root) to root owner

        Args:
            path(Path): path to be chown

        Raises:
            InvalidPath: if path does not belong to root
        """
        def set_owner(current: Path) -> None:
            uid, gid = self.owner(current)
            if uid == root_uid and gid == root_gid:
                return
            os.chown(current, root_uid, root_gid, follow_symlinks=False)

        if self.root not in path.parents:
            raise InvalidPath(path, self.root)
        root_uid, root_gid = self.root_owner
        while path != self.root:
            set_owner(path)
            path = path.parent

    def tree_clear(self, package_base: str) -> None:
        """
        clear package specific files

        Args:
            package_base(str): package base name
        """
        for directory in (
                self.cache_for(package_base),
        ):
            shutil.rmtree(directory, ignore_errors=True)

    def tree_create(self) -> None:
        """
        create ahriman working tree
        """
        for directory in (
                self.cache,
                self.chroot,
                self.packages,
                self.repository,
        ):
            directory.mkdir(mode=0o755, parents=True, exist_ok=True)
            self.chown(directory)
