#
# Copyright (c) 2021-2025 ahriman team.
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

from enum import StrEnum


class UploadSettings(StrEnum):
    """
    remote synchronization targets enumeration

    Attributes:
        Disabled(UploadSettings): (class attribute) no sync will be performed, required for testing purpose
        Rsync(UploadSettings): (class attribute) sync via rsync
        S3(UploadSettings): (class attribute) sync to Amazon S3
        GitHub(UploadSettings): (class attribute) sync to GitHub releases page
        RemoteService(UploadSettings): (class attribute) sync to another ahriman instance
    """

    Disabled = "disabled"  # for testing purpose
    Rsync = "rsync"
    S3 = "s3"
    GitHub = "github"
    RemoteService = "remote-service"

    @staticmethod
    def from_option(value: str) -> UploadSettings:
        """
        construct value from configuration

        Args:
            value(str): configuration value

        Returns:
            UploadSettings: parsed value
        """
        match value.lower():
            case "rsync":
                return UploadSettings.Rsync
            case "s3":
                return UploadSettings.S3
            case "github":
                return UploadSettings.GitHub
            case "ahriman" | "remote-service":
                return UploadSettings.RemoteService
            case _:
                return UploadSettings.Disabled
