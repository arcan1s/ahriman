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

import logging

from pathlib import Path
from typing import Iterable, Type

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import SyncFailed
from ahriman.models.package import Package
from ahriman.models.upload_settings import UploadSettings


class Upload:
    """
    base remote sync class
    :ivar architecture: repository architecture
    :ivar configuration: configuration instance
    :ivar logger: application logger
    """

    def __init__(self, architecture: str, configuration: Configuration) -> None:
        """
        default constructor
        :param architecture: repository architecture
        :param configuration: configuration instance
        """
        self.logger = logging.getLogger("builder")
        self.architecture = architecture
        self.config = configuration

    @classmethod
    def load(cls: Type[Upload], architecture: str, configuration: Configuration, target: str) -> Upload:
        """
        load client from settings
        :param architecture: repository architecture
        :param configuration: configuration instance
        :param target: target to run sync (e.g. s3)
        :return: client according to current settings
        """
        provider = UploadSettings.from_option(target)
        if provider == UploadSettings.Rsync:
            from ahriman.core.upload.rsync import Rsync
            return Rsync(architecture, configuration)
        if provider == UploadSettings.S3:
            from ahriman.core.upload.s3 import S3
            return S3(architecture, configuration)
        return cls(architecture, configuration)  # should never happen

    def run(self, path: Path, built_packages: Iterable[Package]) -> None:
        """
        run remote sync
        :param path: local path to sync
        :param built_packages: list of packages which has just been built
        """
        try:
            self.sync(path, built_packages)
        except Exception:
            self.logger.exception("remote sync failed")
            raise SyncFailed()

    def sync(self, path: Path, built_packages: Iterable[Package]) -> None:
        """
        sync data to remote server
        :param path: local path to sync
        :param built_packages: list of packages which has just been built
        """
