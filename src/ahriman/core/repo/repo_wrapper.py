#
# Copyright (c) 2021 Evgenii Alekseev.
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
import os

from typing import List

from ahriman.core.exceptions import BuildFailed
from ahriman.core.util import check_output
from ahriman.models.repository_paths import RepositoryPaths


class RepoWrapper:

    def __init__(self, name: str, paths: RepositoryPaths, sign_args: List[str]) -> None:
        self.logger = logging.getLogger('build_details')
        self.name = name
        self.paths = paths
        self.sign_args = sign_args

    @property
    def repo_path(self) -> str:
        return os.path.join(self.paths.repository, f'{self.name}.db.tar.gz')

    def add(self, path: str) -> None:
        check_output(
            'repo-add', *self.sign_args, '-R', self.repo_path, path,
            exception=BuildFailed(path),
            cwd=self.paths.repository,
            logger=self.logger)

    def remove(self, prefix: str, package: str) -> None:
        for fn in filter(lambda f: f.startswith(prefix), os.listdir(self.paths.repository)):
            full_path = os.path.join(self.paths.repository, fn)
            os.remove(full_path)
        check_output(
            'repo-remove', *self.sign_args, self.repo_path, package,
            exception=BuildFailed(package),
            cwd=self.paths.repository,
            logger=self.logger)
