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
from dataclasses import dataclass
from typing import Optional

from ahriman.core.exceptions import InvalidOption


@dataclass
class PackageDescription:
    '''
    package specific properties
    '''
    filename: Optional[str] = None
    installed_size: Optional[int] = None

    @staticmethod
    def size_to_str(size: Optional[float], level: int = 0) -> str:
        '''
        convert size to string
        :param size: size to convert
        :param level: represents current units, 0 is B, 1 is KiB etc
        :return: pretty printable size as string
        '''
        def str_level() -> str:
            if level == 0:
                return 'B'
            elif level == 1:
                return 'KiB'
            elif level == 2:
                return 'MiB'
            elif level == 3:
                return 'GiB'
            raise InvalidOption(level)

        if size is None:
            return ''
        elif size < 1024:
            return f'{round(size, 2)} {str_level()}'
        return PackageDescription.size_to_str(size / 1024, level + 1)
