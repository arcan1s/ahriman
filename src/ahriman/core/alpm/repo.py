#
# Copyright (c) 2021 ahriman team.
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
import logging

from pathlib import Path
from typing import List

from ahriman.core.exceptions import BuildFailed
from ahriman.core.util import check_output
from ahriman.models.repository_paths import RepositoryPaths


class Repo:
    """
    repo-add and repo-remove wrapper
    :ivar logger: class logger
    :ivar name: repository name
    :ivar paths: repository paths instance
    :ivar sign_args: additional args which have to be used to sign repository archive
    """

    _check_output = check_output

    def __init__(self, name: str, paths: RepositoryPaths, sign_args: List[str]) -> None:
        """
        default constructor
        :param name: repository name
        :param paths: repository paths instance
        :param sign_args: additional args which have to be used to sign repository archive
        """
        self.logger = logging.getLogger("build_details")
        self.name = name
        self.paths = paths
        self.sign_args = sign_args

    @property
    def repo_path(self) -> Path:
        """
        :return: path to repository database
        """
        return self.paths.repository / f"{self.name}.db.tar.gz"

    def add(self, path: Path) -> None:
        """
        add new package to repository
        :param path: path to archive to add
        """
        Repo._check_output(
            "repo-add", *self.sign_args, "-R", str(self.repo_path), str(path),
            exception=BuildFailed(path.name),
            cwd=self.paths.repository,
            logger=self.logger)

    def remove(self, package: str, filename: Path) -> None:
        """
        remove package from repository
        :param package: package name to remove
        :param filename: package filename to remove
        """
        # remove package and signature (if any) from filesystem
        for full_path in self.paths.repository.glob(f"{filename}*"):
            full_path.unlink()

        # remove package from registry
        Repo._check_output(
            "repo-remove", *self.sign_args, str(self.repo_path), package,
            exception=BuildFailed(package),
            cwd=self.paths.repository,
            logger=self.logger)
