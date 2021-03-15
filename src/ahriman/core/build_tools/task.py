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
    '''
    base package build task
    :ivar build_logger: logger for build process
    :ivar logger: class logger
    :ivar package: package definitions
    :ivar paths: repository paths instance
    '''

    def __init__(self, package: Package, architecture: str, config: Configuration, paths: RepositoryPaths) -> None:
        '''
        default constructor
        :param package: package definitions
        :param architecture: repository architecture
        :param config: configuration instance
        :param paths: repository paths instance
        '''
        self.logger = logging.getLogger('builder')
        self.build_logger = logging.getLogger('build_details')
        self.package = package
        self.paths = paths

        section = config.get_section_name('build', architecture)
        self.archbuild_flags = config.getlist(section, 'archbuild_flags')
        self.build_command = config.get(section, 'build_command')
        self.makepkg_flags = config.getlist(section, 'makepkg_flags')
        self.makechrootpkg_flags = config.getlist(section, 'makechrootpkg_flags')

    @property
    def cache_path(self) -> str:
        '''
        :return: path to cached packages
        '''
        return os.path.join(self.paths.cache, self.package.base)

    @property
    def git_path(self) -> str:
        '''
        :return: path to clone package from git
        '''
        return os.path.join(self.paths.sources, self.package.base)

    @staticmethod
    def fetch(local: str, remote: str, branch: str = 'master') -> None:
        '''
        either clone repository or update it to origin/`branch`
        :param local: local path to fetch
        :param remote: remote target (from where to fetch)
        :param branch: branch name to checkout, master by default
        '''
        if os.path.isdir(local):
            check_output('git', 'fetch', 'origin', branch, cwd=local, exception=None)
        else:
            check_output('git', 'clone', remote, local, exception=None)
        # and now force reset to our branch
        check_output('git', 'reset', '--hard', f'origin/{branch}', cwd=local, exception=None)

    def build(self) -> List[str]:
        '''
        run package build
        :return: paths of produced packages
        '''
        cmd = [self.build_command, '-r', self.paths.chroot]
        cmd.extend(self.archbuild_flags)
        cmd.extend(['--'] + self.makechrootpkg_flags)
        cmd.extend(['--'] + self.makepkg_flags)
        self.logger.info(f'using {cmd} for {self.package.base}')

        check_output(
            *cmd,
            exception=BuildFailed(self.package.base),
            cwd=self.git_path,
            logger=self.build_logger)

        # well it is not actually correct, but we can deal with it
        return check_output('makepkg', '--packagelist',
                            exception=BuildFailed(self.package.base),
                            cwd=self.git_path).splitlines()

    def init(self, path: Optional[str] = None) -> None:
        '''
        fetch package from git
        :param path: optional local path to fetch. If not set default path will be used
        '''
        git_path = path or self.git_path
        if os.path.isdir(self.cache_path):
            # no need to clone whole repository, just copy from cache first
            shutil.copytree(self.cache_path, git_path)
        return Task.fetch(git_path, self.package.git_url)
