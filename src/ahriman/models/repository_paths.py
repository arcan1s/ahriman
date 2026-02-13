#
# Copyright (c) 2021-2026 ahriman team.
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
import contextlib
import os
import shutil

from collections.abc import Iterator
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from pwd import getpwuid
from typing import ParamSpec

from ahriman.core.log import LazyLogging
from ahriman.core.utils import owner
from ahriman.models.repository_id import RepositoryId


Params = ParamSpec("Params")


@dataclass(frozen=True)
class RepositoryPaths(LazyLogging):
    """
    repository paths holder. For the most operations with paths you want to use this object

    Attributes:
        repository_id(RepositoryId): repository unique identifier
        root(Path): repository root (i.e. ahriman home)

    Examples:
        This class can be used in order to access the repository tree structure::

            >>> paths = RepositoryPaths(Path("/var/lib/ahriman"), RepositoryId("x86_64", "aur"))

        Additional methods can be used in order to ensure that tree is created::

            >>> paths.tree_create()

        Access to directories inside can be done by either using properties or specifying the package base::

            >>> cache_dir = paths.cache
            >>> ahriman_cache_dir = paths.cache_for("ahriman")
    """

    root: Path
    repository_id: RepositoryId
    _force_current_tree: bool = field(default=False, kw_only=True)

    @property
    def _repository_root(self) -> Path:
        """
        repository root which can be used for invalid (not fully loaded instances)

        Returns:
            Path: root path to repositories
        """
        return self.root / "repository"

    @cached_property
    def _suffix(self) -> Path:
        """
        suffix of the paths as defined by repository structure

        Returns:
            Path: relative path which contains only architecture segment in case if legacy tree is used and repository
            name and architecture otherwise
        """
        if not self._force_current_tree:
            if (self._repository_root / self.repository_id.architecture).is_dir():
                self.logger.warning("using legacy per architecture tree")
                return Path(self.repository_id.architecture)  # legacy tree suffix
        return Path(self.repository_id.name) / self.repository_id.architecture

    @property
    def archive(self) -> Path:
        """
        archive directory root

        Returns:
            Path: archive directory root
        """
        return self.root / "archive"

    @property
    def build_root(self) -> Path:
        """
        same as :attr:`chroot`, but exactly build chroot

        Returns:
            Path: path to directory in which build process is run
        """
        uid, _ = owner(self.root)
        return self.chroot / f"{self.repository_id.name}-{self.repository_id.architecture}" / getpwuid(uid).pw_name

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
        # for the chroot directory devtools will create own tree, and we don't have to specify architecture here
        return self.root / "chroot" / self.repository_id.name

    @property
    def packages(self) -> Path:
        """
        get directory for built packages

        Returns:
            Path: full path to built packages directory
        """
        return self.root / "packages" / self._suffix

    @property
    def pacman(self) -> Path:
        """
        get directory for pacman local package cache

        Returns:
            Path: full path to pacman local database cache
        """
        return self.root / "pacman" / self._suffix

    @property
    def repository(self) -> Path:
        """
        get repository directory

        Returns:
            Path: full path to the repository directory
        """
        return self._repository_root / self._suffix

    @property
    def root_owner(self) -> tuple[int, int]:
        """
        get UID and GID of the root directory

        Returns:
            tuple[int, int]: owner user and group of the root directory
        """
        return owner(self.root)

    # pylint: disable=protected-access
    @classmethod
    def known_architectures(cls, root: Path, name: str = "") -> set[str]:
        """
        get known architecture names

        Args:
            root(Path): repository root
            name(str, optional): repository name (Default value = "")

        Returns:
            set[str]: list of repository architectures for which there is created tree
        """
        def walk(repository_dir: Path) -> Iterator[str]:
            for architecture in filter(lambda path: path.is_dir(), repository_dir.iterdir()):
                yield architecture.name

        instance = cls(root, RepositoryId("", ""))
        match (instance._repository_root / name):
            case full_tree if full_tree.is_dir():
                return set(walk(full_tree))  # actually works for legacy too in case if name is set to empty string
            case _ if instance._repository_root.is_dir():
                return set(walk(instance._repository_root))  # legacy only tree
            case _:
                return set()  # no tree detected at all

    # pylint: disable=protected-access
    @classmethod
    def known_repositories(cls, root: Path) -> set[str]:
        """
        get known repository names

        Args:
            root(Path): repository root

        Returns:
            set[str]: list of repository names for which there is created tree. Returns empty set in case if repository
            is loaded in legacy mode
        """
        # simply walk through the root. In case if there are subdirectories, emit the name
        def walk(paths: RepositoryPaths) -> Iterator[str]:
            for repository in filter(lambda path: path.is_dir(), paths._repository_root.iterdir()):
                if any(path.is_dir() for path in repository.iterdir()):
                    yield repository.name

        instance = cls(root, RepositoryId("", ""))
        if not instance._repository_root.is_dir():
            return set()  # no tree created

        return set(walk(instance))

    def archive_for(self, package_base: str) -> Path:
        """
        get path to archive specified search criteria

        Args:
            package_base(str): package base name

        Returns:
            Path: path to archive directory for package base
        """
        return self.archive / "packages" / package_base[0] / package_base

    def cache_for(self, package_base: str) -> Path:
        """
        get path to cached PKGBUILD and package sources for the package base

        Args:
            package_base(str): package base name

        Returns:
            Path: full path to directory for specified package base cache
        """
        return self.cache / package_base

    def ensure_exists(self, directory: Path) -> Path:
        """
        get path based on ``directory`` callable provided and ensure it exists

        Args:
            directory(Path): path to directory to check

        Returns:
            Path: original path based on extractor provided. Directory will always exist

        Examples:
            This method calls directory accessor and then checks if there is a directory and - otherwise - creates it::

                >>> paths.ensure_exists(paths.archive_for(package_base))
        """
        if not directory.is_dir():
            with self.preserve_owner():
                directory.mkdir(mode=0o755, parents=True)

        return directory

    @contextlib.contextmanager
    def preserve_owner(self) -> Iterator[None]:
        """
        perform any action preserving owner for any newly created file or directory

        Examples:
            This method is designed to use as context manager when you are going to perform operations which might
            change filesystem, especially if you are doing it under unsafe flag, e.g.::

                >>> with paths.preserve_owner():
                >>>     paths.tree_create()

            Note, however, that this method doesn't handle any exceptions and will eventually interrupt
            if there will be any.
        """
        # guard non-root
        # the reason we do this is that it only works if permissions can be actually changed. Hence,
        # non-privileged user (e.g. personal user or ahriman user) can't change permissions.
        # The only one who can do so is root, so if user is not root we just terminate function
        current_uid, current_gid = os.geteuid(), os.getegid()
        if current_uid != 0:
            yield
            return

        # set uid and gid to root owner
        target_uid, target_gid = self.root_owner
        os.setegid(target_gid)
        os.seteuid(target_uid)

        try:
            yield
        finally:
            # reset uid and gid
            os.seteuid(current_uid)
            os.setegid(current_gid)

    def tree_clear(self, package_base: str) -> None:
        """
        clear package specific files

        Args:
            package_base(str): package base name
        """
        for directory in (
                self.cache_for(package_base),
                self.archive_for(package_base),
        ):
            shutil.rmtree(directory, ignore_errors=True)

    def tree_create(self) -> None:
        """
        create ahriman working tree
        """
        if self.repository_id.is_empty:
            return  # do not even try to create tree in case if no repository id set

        for directory in (
            self.archive,
            self.cache,
            self.chroot,
            self.packages,
            self.pacman,
            self.repository,
        ):
            self.ensure_exists(directory)
