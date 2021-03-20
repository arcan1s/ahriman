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

import datetime

from enum import Enum
from typing import Any, Dict, Optional, Type, Union

from ahriman.core.util import pretty_datetime


class BuildStatusEnum(Enum):
    '''
    build status enumeration
    :cvar Unknown: build status is unknown
    :cvar Pending: package is out-of-dated and will be built soon
    :cvar Building: package is building right now
    :cvar Failed: package build failed
    :cvar Success: package has been built without errors
    '''

    Unknown = 'unknown'
    Pending = 'pending'
    Building = 'building'
    Failed = 'failed'
    Success = 'success'

    def badges_color(self) -> str:
        '''
        convert itself to shield.io badges color
        :return: shields.io color
        '''
        if self == BuildStatusEnum.Pending:
            return 'yellow'
        if self == BuildStatusEnum.Building:
            return 'yellow'
        if self == BuildStatusEnum.Failed:
            return 'critical'
        if self == BuildStatusEnum.Success:
            return 'success'
        return 'inactive'


class BuildStatus:
    '''
    build status holder
    :ivar status: build status
    :ivar _timestamp: build status update time
    '''

    def __init__(self, status: Union[BuildStatusEnum, str, None] = None,
                 timestamp: Optional[int] = None) -> None:
        '''
        default constructor
        :param status: current build status if known. `BuildStatusEnum.Unknown` will be used if not set
        :param timestamp: build status timestamp. Current timestamp will be used if not set
        '''
        self.status = BuildStatusEnum(status) if status else BuildStatusEnum.Unknown
        self.timestamp = timestamp or int(datetime.datetime.utcnow().timestamp())

    @classmethod
    def from_json(cls: Type[BuildStatus], dump: Dict[str, Any]) -> BuildStatus:
        '''
        construct status properties from json dump
        :param dump: json dump body
        :return: status properties
        '''
        return cls(dump.get('status'), dump.get('timestamp'))

    def pretty_print(self) -> str:
        '''
        generate pretty string representation
        :return: print-friendly string
        '''
        return f'{self.status.value} ({pretty_datetime(self.timestamp)})'

    def view(self) -> Dict[str, Any]:
        '''
        generate json status view
        :return: json-friendly dictionary
        '''
        return {
            'status': self.status.value,
            'timestamp': self.timestamp
        }

    def __repr__(self) -> str:
        '''
        generate string representation of object
        :return: unique string representation
        '''
        return f'BuildStatus(status={self.status.value}, timestamp={self.timestamp})'
