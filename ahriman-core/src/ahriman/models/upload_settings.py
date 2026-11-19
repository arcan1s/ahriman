#
# Copyright (c) 2021-2026 ahriman team.
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
from enum import StrEnum


class UploadSettings(StrEnum):
    """
    remote synchronization targets enumeration

    Attributes:
        DISABLED(UploadSettings): no sync will be performed, required for testing purpose
        RSYNC(UploadSettings): sync via rsync
        S3(UploadSettings): sync to Amazon S3
        GITHUB(UploadSettings): sync to GitHub releases page
        REMOTE_SERVICE(UploadSettings): sync to another ahriman instance
    """

    DISABLED = "disabled"  # for testing purpose
    RSYNC = "rsync"
    S3 = "s3"
    GITHUB = "github"
    REMOTE_SERVICE = "remote-service"

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
                return UploadSettings.RSYNC
            case "s3":
                return UploadSettings.S3
            case "github":
                return UploadSettings.GITHUB
            case "ahriman" | "remote-service":
                return UploadSettings.REMOTE_SERVICE
            case _:
                return UploadSettings.DISABLED
