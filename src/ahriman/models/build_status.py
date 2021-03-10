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
    Unknown = 'unknown'
    Pending = 'pending'
    Building = 'building'
    Failed = 'failed'
    Success = 'success'


class BuildStatus:

    def __init__(self, status: Union[BuildStatusEnum, str, None] = None,
                 timestamp: Optional[datetime.datetime] = None) -> None:
        self.status = BuildStatusEnum(status) if status else BuildStatusEnum.Unknown
        self._timestamp = timestamp or datetime.datetime.utcnow()

    @property
    def timestamp(self) -> str:
        return self._timestamp.strftime('%Y-%m-%d %H:%M:%S')
