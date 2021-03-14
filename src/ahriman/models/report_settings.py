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
from __future__ import annotations

from enum import Enum, auto

from ahriman.core.exceptions import InvalidOption


class ReportSettings(Enum):
    '''
    report targets enumeration
    :ivar HTML: html report generation
    '''

    HTML = auto()

    @staticmethod
    def from_option(value: str) -> ReportSettings:
        '''
        construct value from configuration
        :param value: configuration value
        :return: parsed value
        '''
        if value.lower() in ('html',):
            return ReportSettings.HTML
        raise InvalidOption(value)
