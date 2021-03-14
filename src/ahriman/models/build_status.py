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
import datetime

from enum import Enum
from typing import Optional, Union


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


class BuildStatus:
    '''
    build status holder
    :ivar status: build status
    :ivar _timestamp: build status update time
    '''

    def __init__(self, status: Union[BuildStatusEnum, str, None] = None,
                 timestamp: Optional[datetime.datetime] = None) -> None:
        '''
        default constructor
        :param status: current build status if known. `BuildStatusEnum.Unknown` will be used if not set
        :param timestamp: build status timestamp. Current timestamp will be used if not set
        '''
        self.status = BuildStatusEnum(status) if status else BuildStatusEnum.Unknown
        self._timestamp = timestamp or datetime.datetime.utcnow()

    @property
    def timestamp(self) -> str:
        '''
        :return: string representation of build status timestamp
        '''
        return self._timestamp.strftime('%Y-%m-%d %H:%M:%S')
