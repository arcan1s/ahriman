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

from typing import Dict, List

from ahriman.core.repository.executor import Executor
from ahriman.core.repository.update_handler import UpdateHandler
from ahriman.core.util import package_like
from ahriman.models.package import Package


class Repository(Executor, UpdateHandler):
    '''
    base repository control class
    '''

    def packages(self) -> List[Package]:
        '''
        generate list of repository packages
        :return: list of packages properties
        '''
        result: Dict[str, Package] = {}
        for fn in os.listdir(self.paths.repository):
            if not package_like(fn):
                continue
            full_path = os.path.join(self.paths.repository, fn)
            try:
                local = Package.load(full_path, self.pacman, self.aur_url)
                result.setdefault(local.base, local).packages.update(local.packages)
            except Exception:
                self.logger.exception(f'could not load package from {fn}', exc_info=True)
                continue
        return list(result.values())

    def packages_built(self) -> List[str]:
        '''
        get list of files in built packages directory
        :return: list of filenames from the directory
        '''
        return [
            os.path.join(self.paths.packages, fn)
            for fn in os.listdir(self.paths.packages)
        ]
