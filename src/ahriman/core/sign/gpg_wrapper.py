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

    def __init__(self, config: Configuration) -> None:
        self.logger = logging.getLogger('build_details')

        self.key = config.get('sign', 'key', fallback=None)
        self.sign = SignSettings.from_option(config.get('sign', 'enabled'))

    @property
    def repository_sign_args(self) -> List[str]:
        if self.sign != SignSettings.SignRepository:
            return []
        return ['--sign', '--key', self.key] if self.key else ['--sign']

    def process(self, path: str) -> List[str]:
        check_output(
            *self.sign_cmd(path),
            exception=BuildFailed(path),
            cwd=os.path.dirname(path),
            logger=self.logger)
        return [path, f'{path}.sig']

    def sign_cmd(self, path: str) -> List[str]:
        cmd = ['gpg']
        if self.key is not None:
            cmd.extend(['-u', self.key])
        cmd.extend(['-b', path])
        return cmd

    def sign_package(self, path: str) -> List[str]:
        if self.sign != SignSettings.SignPackages:
            return [path]
        return self.process(path)

    def sign_repository(self, path: str) -> List[str]:
        if self.sign != SignSettings.SignRepository:
            return [path]
        return self.process(path)