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
import logging

from pathlib import Path

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import SyncFailed
from ahriman.models.upload_settings import UploadSettings


class Uploader:
    """
    base remote sync class
    :ivar architecture: repository architecture
    :ivar config: configuration instance
    :ivar logger: application logger
    """

    def __init__(self, architecture: str, config: Configuration) -> None:
        """
        default constructor
        :param architecture: repository architecture
        :param config: configuration instance
        """
        self.logger = logging.getLogger("builder")
        self.architecture = architecture
        self.config = config

    @staticmethod
    def run(architecture: str, config: Configuration, target: str, path: Path) -> None:
        """
        run remote sync
        :param architecture: repository architecture
        :param config: configuration instance
        :param target: target to run sync (e.g. s3)
        :param path: local path to sync
        """
        provider = UploadSettings.from_option(target)
        if provider == UploadSettings.Rsync:
            from ahriman.core.upload.rsync import Rsync
            uploader: Uploader = Rsync(architecture, config)
        elif provider == UploadSettings.S3:
            from ahriman.core.upload.s3 import S3
            uploader = S3(architecture, config)
        else:
            uploader = Uploader(architecture, config)

        try:
            uploader.sync(path)
        except Exception:
            uploader.logger.exception(f"remote sync failed for {provider.name}")
            raise SyncFailed()

    def sync(self, path: Path) -> None:
        """
        sync data to remote server
        :param path: local path to sync
        """
