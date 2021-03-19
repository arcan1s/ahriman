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

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import BuildFailed
from ahriman.core.util import check_output
from ahriman.models.sign_settings import SignSettings


class GPG:
    '''
    gnupg wrapper
    :ivar architecture: repository architecture
    :ivar config: configuration instance
    :ivar default_key: default PGP key ID to use
    :ivar logger: class logger
    :ivar target: list of targets to sign (repository, package etc)
    '''

    def __init__(self, architecture: str, config: Configuration) -> None:
        '''
        default constructor
        :param architecture: repository architecture
        :param config: configuration instance
        '''
        self.logger = logging.getLogger('build_details')
        self.config = config
        self.section = config.get_section_name('sign', architecture)
        self.target = [SignSettings.from_option(opt) for opt in config.getlist(self.section, 'target')]
        self.default_key = config.get(self.section, 'key') if self.target else ''

    @property
    def repository_sign_args(self) -> List[str]:
        '''
        :return: command line arguments for repo-add command to sign database
        '''
        if SignSettings.SignRepository not in self.target:
            return []
        return ['--sign', '--key', self.default_key]

    @staticmethod
    def sign_cmd(path: str, key: str) -> List[str]:
        '''
        gpg command to run
        :param path: path to file to sign
        :param key: PGP key ID
        :return: gpg command with all required arguments
        '''
        return ['gpg', '-u', key, '-b', path]

    def process(self, path: str, key: str) -> List[str]:
        '''
        gpg command wrapper
        :param path: path to file to sign
        :param key: PGP key ID
        :return: list of generated files including original file
        '''
        check_output(
            *GPG.sign_cmd(path, key),
            exception=BuildFailed(path),
            cwd=os.path.dirname(path),
            logger=self.logger)
        return [path, f'{path}.sig']

    def sign_package(self, path: str, base: str) -> List[str]:
        '''
        sign package if required by configuration
        :param path: path to file to sign
        :param base: package base required to check for key overrides
        :return: list of generated files including original file
        '''
        if SignSettings.SignPackages not in self.target:
            return [path]
        key = self.config.get(self.section, f'key_{base}', fallback=self.default_key)
        return self.process(path, key)

    def sign_repository(self, path: str) -> List[str]:
        '''
        sign repository if required by configuration
        :note: more likely you just want to pass `repository_sign_args` to repo wrapper
        :param path: path to repository database
        :return: list of generated files including original file
        '''
        if SignSettings.SignRepository not in self.target:
            return [path]
        return self.process(path, self.default_key)
