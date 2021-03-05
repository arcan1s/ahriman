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
import logging

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import SyncFailed
from ahriman.models.upload_settings import UploadSettings


class Uploader:

    def __init__(self, config: Configuration) -> None:
        self.config = config
        self.logger = logging.getLogger('builder')

    @staticmethod
    def run(config: Configuration, path: str) -> None:
        provider = UploadSettings.from_option(config.get('upload', 'enabled'))
        if provider == UploadSettings.Rsync:
            from ahriman.core.upload.rsync import Rsync
            uploader: Uploader = Rsync(config)
        elif provider == UploadSettings.S3:
            from ahriman.core.upload.s3 import S3
            uploader = S3(config)
        else:
            from ahriman.core.upload.dummy import Dummy
            uploader = Dummy(config)

        try:
            uploader.sync(path)
        except Exception as e:
            raise SyncFailed from e

    def sync(self, path: str) -> None:
        raise NotImplementedError
