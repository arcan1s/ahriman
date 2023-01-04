#
# Copyright (c) 2021-2023 ahriman team.
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

from enum import Enum
from typing import Type


class UploadSettings(str, Enum):
    """
    remote synchronization targets enumeration

    Attributes:
        Disabled(UploadSettings): (class attribute) no sync will be performed, required for testing purpose
        Rsync(UploadSettings): (class attribute) sync via rsync
        S3(UploadSettings): (class attribute) sync to Amazon S3
        Github(UploadSettings): (class attribute) sync to github releases page
    """

    Disabled = "disabled"  # for testing purpose
    Rsync = "rsync"
    S3 = "s3"
    Github = "github"

    @classmethod
    def from_option(cls: Type[UploadSettings], value: str) -> UploadSettings:
        """
        construct value from configuration

        Args:
            value(str): configuration value

        Returns:
            UploadSettings: parsed value
        """
        if value.lower() in ("rsync",):
            return cls.Rsync
        if value.lower() in ("s3",):
            return cls.S3
        if value.lower() in ("github",):
            return cls.Github
        return cls.Disabled
