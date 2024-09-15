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
from pathlib import Path

from ahriman.core.exceptions import BuildError
from ahriman.core.log import LazyLogging
from ahriman.core.utils import check_output
from ahriman.models.repository_paths import RepositoryPaths


class Repo(LazyLogging):
    """
    repo-add and repo-remove wrapper

    Attributes:
        name(str): repository name
        paths(RepositoryPaths): repository paths instance
        sign_args(list[str]): additional args which have to be used to sign repository archive
        uid(int): uid of the repository owner user
    """

    def __init__(self, name: str, paths: RepositoryPaths, sign_args: list[str]) -> None:
        """
        Args:
            name(str): repository name
            paths(RepositoryPaths): repository paths instance
            sign_args(list[str]): additional args which have to be used to sign repository archive
        """
        self.name = name
        self.paths = paths
        self.uid, _ = paths.root_owner
        self.sign_args = sign_args

    @property
    def repo_path(self) -> Path:
        """
        get full path to the repository database

        Returns:
            Path: path to repository database
        """
        return self.paths.repository / f"{self.name}.db.tar.gz"

    def add(self, path: Path) -> None:
        """
        add new package to repository

        Args:
            path(Path): path to archive to add
        """
        check_output(
            "repo-add", *self.sign_args, "--remove", str(self.repo_path), str(path),
            exception=BuildError.from_process(path.name),
            cwd=self.paths.repository,
            logger=self.logger,
            user=self.uid)

    def init(self) -> None:
        """
        create empty repository database. It just calls add with empty arguments
        """
        # since pacman-6.1.0 repo-add doesn't create empty database in case if no packages supplied
        # this code creates empty files instead
        if self.repo_path.exists():
            return  # database is already created, skip this part

        self.repo_path.touch(exist_ok=True)
        (self.paths.repository / f"{self.name}.db").symlink_to(self.repo_path)

    def remove(self, package: str, filename: Path) -> None:
        """
        remove package from repository

        Args:
            package(str): package name to remove
            filename(Path): package filename to remove
        """
        # remove package and signature (if any) from filesystem
        for full_path in self.paths.repository.glob(f"{filename}*"):
            full_path.unlink()

        # remove package from registry
        check_output(
            "repo-remove", *self.sign_args, str(self.repo_path), package,
            exception=BuildError.from_process(package),
            cwd=self.paths.repository,
            logger=self.logger,
            user=self.uid)
