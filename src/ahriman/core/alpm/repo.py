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
        root(Path): repository root
        sign_args(list[str]): additional args which have to be used to sign repository archive
        uid(int): uid of the repository owner user
    """

    def __init__(self, name: str, paths: RepositoryPaths, sign_args: list[str], root: Path | None = None) -> None:
        """
        Args:
            name(str): repository name
            paths(RepositoryPaths): repository paths instance
            sign_args(list[str]): additional args which have to be used to sign repository archive
            root(Path | None, optional): repository root. If none set, the default will be used (Default value = None)
        """
        self.name = name
        self.root = root or paths.repository
        self.uid, _ = paths.root_owner
        self.sign_args = sign_args

    @property
    def repo_path(self) -> Path:
        """
        get full path to the repository database

        Returns:
            Path: path to repository database
        """
        return self.root / f"{self.name}.db.tar.gz"

    def add(self, path: Path, *, remove: bool = True) -> None:
        """
        add new package to repository

        Args:
            path(Path): path to archive to add
            remove(bool, optional): whether to remove old packages or not (Default value = True)
        """
        command = ["repo-add", *self.sign_args]
        if remove:
            command.extend(["--remove"])
        command.extend([str(self.repo_path), str(path)])

        # add to repository
        check_output(
            *command,
            exception=BuildError.from_process(path.name),
            cwd=self.root,
            logger=self.logger,
            user=self.uid,
        )

    def init(self) -> None:
        """
        create empty repository database. It just calls add with empty arguments
        """
        check_output("repo-add", *self.sign_args, str(self.repo_path),
                     cwd=self.root, logger=self.logger, user=self.uid)

    def remove(self, package_name: str | None, filename: Path) -> None:
        """
        remove package from repository

        Args:
            package_name(str | None): package name to remove. If none set, it will be guessed from filename
            filename(Path): package filename to remove
        """
        package_name = package_name or filename.name.rsplit("-", maxsplit=3)[0]

        # remove package and signature (if any) from filesystem
        for full_path in self.root.glob(f"**/{filename.name}*"):
            full_path.unlink()

        # remove package from registry
        check_output(
            "repo-remove", *self.sign_args, str(self.repo_path), package_name,
            exception=BuildError.from_process(package_name),
            cwd=self.root,
            logger=self.logger,
            user=self.uid,
        )
