#
# Copyright (c) 2021 ahriman team.
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
from typing import Type

from ahriman.core.exceptions import InvalidOption


class UploadSettings(Enum):
    """
    remote synchronization targets enumeration
    :cvar Rsync: sync via rsync
    :cvar S3: sync to Amazon S3
    """

    Disabled = auto()  # for testing purpose
    Rsync = auto()
    S3 = auto()

    @classmethod
    def from_option(cls: Type[UploadSettings], value: str) -> UploadSettings:
        """
        construct value from configuration
        :param value: configuration value
        :return: parsed value
        """
        if value.lower() in ("rsync",):
            return cls.Rsync
        if value.lower() in ("s3",):
            return cls.S3
        raise InvalidOption(value)
