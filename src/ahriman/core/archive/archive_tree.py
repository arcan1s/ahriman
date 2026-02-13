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
import datetime

from collections.abc import Iterator
from pathlib import Path

from ahriman.core.alpm.repo import Repo
from ahriman.core.log import LazyLogging
from ahriman.core.utils import package_like, symlink_relative, utcnow, walk
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription
from ahriman.models.repository_paths import RepositoryPaths


class ArchiveTree(LazyLogging):
    """
    wrapper around archive tree

    Attributes:
        paths(RepositoryPaths): repository paths instance
        repository_id(RepositoryId): repository unique identifier
        sign_args(list[str]): additional args which have to be used to sign repository archive
    """

    def __init__(self, repository_path: RepositoryPaths, sign_args: list[str]) -> None:
        """
        Args:
            repository_path(RepositoryPaths): repository paths instance
            sign_args(list[str]): additional args which have to be used to sign repository archive
        """
        self.paths = repository_path
        self.repository_id = repository_path.repository_id
        self.sign_args = sign_args

    def _package_symlinks_create(self, package_description: PackageDescription, root: Path, archive: Path) -> bool:
        """
        process symlinks creation for single package

        Args:
            package_description(PackageDescription): archive descriptor
            root(Path): path to the archive repository root
            archive(Path): path to directory with archives

        Returns:
            bool: ``True`` if symlinks were created and ``False`` otherwise
        """
        symlinks_created = False
        # here we glob for archive itself and signature if any
        for file in archive.glob(f"{package_description.filename}*"):
            try:
                symlink_relative(root / file.name, file)
                symlinks_created = True
            except FileExistsError:
                continue  # symlink is already created, skip processing

        return symlinks_created

    def _repo(self, root: Path) -> Repo:
        """
        constructs :class:`ahriman.core.alpm.repo.Repo` object for given path

        Args:
            root(Path): root of the repository

        Returns:
            Repo: constructed object with correct properties
        """
        return Repo(self.repository_id.name, self.paths, self.sign_args, root)

    def directories_fix(self, paths: set[Path]) -> None:
        """
        remove empty repository directories recursively

        Args:
            paths(set[Path]): repositories to check
        """
        root = self.paths.archive / "repos"
        for repository in paths:
            parents = [repository] + list(repository.parents[:-1])
            for parent in parents:
                path = root / parent
                if not list(path.iterdir()):
                    path.rmdir()

    def repository_for(self, date: datetime.date | None = None) -> Path:
        """
        get full path to repository at the specified date

        Args:
            date(datetime.date | None, optional): date to generate path. If none supplied then today will be used
                (Default value = None)

        Returns:
            Path: path to the repository root
        """
        date = date or utcnow().date()
        return (
            self.paths.archive
            / "repos"
            / date.strftime("%Y")
            / date.strftime("%m")
            / date.strftime("%d")
            / self.repository_id.name
            / self.repository_id.architecture
        )

    def symlinks_create(self, packages: list[Package]) -> None:
        """
        create symlinks for the specified packages in today's repository

        Args:
            packages(list[Package]): list of packages to be updated
        """
        root = self.repository_for()
        repo = self._repo(root)

        for package in packages:
            archive = self.paths.archive_for(package.base)

            for package_name, single in package.packages.items():
                if single.filename is None:
                    self.logger.warning("received empty package filename for %s", package_name)
                    continue

                if self._package_symlinks_create(single, root, archive):
                    repo.add(root / single.filename)

    def symlinks_fix(self) -> Iterator[Path]:
        """
        remove broken symlinks across repositories for all dates

        Yields:
            Path: path of the sub-repository with removed symlinks
        """
        for path in walk(self.paths.archive / "repos"):
            root = path.parent
            *_, name, architecture = root.parts
            if self.repository_id.name != name or self.repository_id.architecture != architecture:
                continue  # we only process same name repositories

            if not package_like(path):
                continue
            if not path.is_symlink():
                continue  # find symlinks only
            if path.exists():
                continue  # filter out not broken symlinks

            # here we don't have access to original archive, so we have to guess name based on archive name
            # normally it should be fine to do so
            package_name = path.name.rsplit("-", maxsplit=3)[0]
            self._repo(root).remove(package_name, path)
            yield path.parent.relative_to(self.paths.archive / "repos")

    def tree_create(self) -> None:
        """
        create repository tree for current repository
        """
        root = self.repository_for()
        if root.exists():
            return

        with self.paths.preserve_owner():
            root.mkdir(0o755, parents=True)
            # init empty repository here
            self._repo(root).init()
