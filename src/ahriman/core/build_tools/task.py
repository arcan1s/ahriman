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
import os
import logging
import shutil

from typing import List, Optional

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import BuildFailed
from ahriman.core.util import check_output
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


class Task:

    def __init__(self, package: Package, config: Configuration, paths: RepositoryPaths) -> None:
        self.logger = logging.getLogger('builder')
        self.build_logger = logging.getLogger('build_details')
        self.package = package
        self.paths = paths

        self.archbuild_flags = config.get('build_tools', 'archbuild_flags').split()
        self.extra_build = config.get('build_tools', 'extra_build')
        self.makepkg_flags = config.get('build_tools', 'makepkg_flags').split()
        self.multilib_build = config.get('build_tools', 'multilib_build')

    @property
    def git_path(self) -> str:
        return os.path.join(self.paths.sources, self.package.name)

    def build(self) -> List[str]:
        build_tool = self.multilib_build if self.package.is_multilib else self.extra_build

        cmd = [build_tool, '-r', self.paths.chroot]
        cmd.extend(self.archbuild_flags)
        if self.makepkg_flags:
            cmd.extend(['--', '--'] + self.makepkg_flags)
        self.logger.info(f'using {cmd} for {self.package.name}')

        check_output(
            *cmd,
            exception=BuildFailed(self.package.name),
            cwd=self.git_path,
            logger=self.build_logger)

        # well it is not actually correct, but we can deal with it
        return check_output('makepkg', '--packagelist',
                            exception=BuildFailed(self.package.name),
                            cwd=self.git_path).splitlines()

    def fetch(self, path: Optional[str] = None) -> None:
        git_path = path or self.git_path
        shutil.rmtree(git_path, ignore_errors=True)
        check_output('git', 'clone', self.package.url, git_path, exception=None)
