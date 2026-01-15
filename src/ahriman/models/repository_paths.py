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
import contextlib
import os
import shutil

from collections.abc import Iterator
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from pwd import getpwuid

from ahriman.core.exceptions import PathError
from ahriman.core.log import LazyLogging
from ahriman.models.repository_id import RepositoryId


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
    def build_root(self) -> Path:
        """
        same as :attr:`chroot`, but exactly build chroot

        Returns:
            Path: path to directory in which build process is run
        """
        uid, _ = self.owner(self.root)
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
        return self.owner(self.root)

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

    @staticmethod
    def owner(path: Path) -> tuple[int, int]:
        """
        retrieve owner information by path

        Args:
            path(Path): path for which extract ids

        Returns:
            tuple[int, int]: owner user and group ids of the directory
        """
        stat = path.stat()
        return stat.st_uid, stat.st_gid

    def _chown(self, path: Path) -> None:
        """
        set owner of path recursively (from root) to root owner

        Notes:
            More likely you don't want to call this method explicitly, consider using :func:`preserve_owner`
            as context manager instead

        Args:
            path(Path): path to be chown

        Raises:
            PathError: if path does not belong to root
        """
        def set_owner(current: Path) -> None:
            uid, gid = self.owner(current)
            if uid == root_uid and gid == root_gid:
                return
            os.chown(current, root_uid, root_gid, follow_symlinks=False)

        if self.root not in path.parents:
            raise PathError(path, self.root)
        root_uid, root_gid = self.root_owner
        while path != self.root:
            set_owner(path)
            path = path.parent

    def cache_for(self, package_base: str) -> Path:
        """
        get path to cached PKGBUILD and package sources for the package base

        Args:
            package_base(str): package base name

        Returns:
            Path: full path to directory for specified package base cache
        """
        return self.cache / package_base

    @contextlib.contextmanager
    def preserve_owner(self, path: Path | None = None) -> Iterator[None]:
        """
        perform any action preserving owner for any newly created file or directory

        Args:
            path(Path | None, optional): use this path as root instead of repository root (Default value = None)

        Examples:
            This method is designed to use as context manager when you are going to perform operations which might
            change filesystem, especially if you are doing it under unsafe flag, e.g.::

                >>> with paths.preserve_owner():
                >>>     paths.tree_create()

            Note, however, that this method doesn't handle any exceptions and will eventually interrupt
            if there will be any.
        """
        path = path or self.root

        def walk(root: Path) -> Iterator[Path]:
            # basically walk, but skipping some content
            for child in root.iterdir():
                yield child
                if child in (self.chroot.parent,):
                    yield from child.iterdir()  # we only yield top-level in chroot directory
                elif child.is_dir():
                    yield from walk(child)

        # get current filesystem and run action
        previous_snapshot = set(walk(path))
        yield

        # get newly created files and directories and chown them
        new_entries = set(walk(path)).difference(previous_snapshot)
        for entry in new_entries:
            self._chown(entry)

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
        if self.repository_id.is_empty:
            return  # do not even try to create tree in case if no repository id set

        with self.preserve_owner():
            for directory in (
                    self.cache,
                    self.chroot,
                    self.packages,
                    self.pacman,
                    self.repository,
            ):
                directory.mkdir(mode=0o755, parents=True, exist_ok=True)
