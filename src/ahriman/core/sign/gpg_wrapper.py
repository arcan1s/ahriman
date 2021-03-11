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


class GPGWrapper:

    def __init__(self, architecture: str, config: Configuration) -> None:
        self.logger = logging.getLogger('build_details')
        self.config = config
        self.section = config.get_section_name('sign', architecture)
        self.target = [SignSettings.from_option(opt) for opt in config.getlist(self.section, 'target')]
        self.default_key = config.get(self.section, 'key') if self.target else ''

    @property
    def repository_sign_args(self) -> List[str]:
        if SignSettings.SignRepository not in self.target:
            return []
        return ['--sign', '--key', self.default_key]

    def process(self, path: str, key: str) -> List[str]:
        check_output(
            *self.sign_cmd(path, key),
            exception=BuildFailed(path),
            cwd=os.path.dirname(path),
            logger=self.logger)
        return [path, f'{path}.sig']

    def sign_cmd(self, path: str, key: str) -> List[str]:
        cmd = ['gpg']
        cmd.extend(['-u', key])
        cmd.extend(['-b', path])
        return cmd

    def sign_package(self, path: str, base: str) -> List[str]:
        if SignSettings.SignPackages not in self.target:
            return [path]
        key = self.config.get(self.section, f'key_{base}', fallback=self.default_key)
        return self.process(path, key)

    def sign_repository(self, path: str) -> List[str]:
        if SignSettings.SignRepository not in self.target:
            return [path]
        return self.process(path, self.default_key)