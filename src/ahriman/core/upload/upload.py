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

from pathlib import Path
from typing import Iterable, Type

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import SynchronizationError
from ahriman.core.log import LazyLogging
from ahriman.models.package import Package
from ahriman.models.upload_settings import UploadSettings


class Upload(LazyLogging):
    """
    base remote sync class

    Attributes:
        architecture(str): repository architecture
        configuration(Configuration): configuration instance

    Examples:
        These classes provide the way to upload packages to remote sources as it is described in their implementations.
        Basic flow includes class instantiating by using the ``load`` method and then calling the ``run`` method which
        wraps any internal exceptions into the ``SyncFailed`` exception::

            >>> from ahriman.core.configuration import Configuration
            >>>
            >>> configuration = Configuration()
            >>> upload = Upload.load("x86_64", configuration, "s3")
            >>> upload.run(configuration.repository_paths.repository, [])

        Or in case if direct access to exception is required, the ``sync`` method can be used::

            >>> try:
            >>>     upload.sync(configuration.repository_paths.repository, [])
            >>> except Exception as exception:
            >>>     handle_exceptions(exception)
    """

    def __init__(self, architecture: str, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
        """
        self.architecture = architecture
        self.configuration = configuration

    @classmethod
    def load(cls: Type[Upload], architecture: str, configuration: Configuration, target: str) -> Upload:
        """
        load client from settings

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            target(str): target to run sync (e.g. s3)

        Returns:
            Upload: client according to current settings
        """
        section, provider_name = configuration.gettype(target, architecture)
        provider = UploadSettings.from_option(provider_name)
        if provider == UploadSettings.Rsync:
            from ahriman.core.upload.rsync import Rsync
            return Rsync(architecture, configuration, section)
        if provider == UploadSettings.S3:
            from ahriman.core.upload.s3 import S3
            return S3(architecture, configuration, section)
        if provider == UploadSettings.Github:
            from ahriman.core.upload.github import Github
            return Github(architecture, configuration, section)
        return cls(architecture, configuration)  # should never happen

    def run(self, path: Path, built_packages: Iterable[Package]) -> None:
        """
        run remote sync

        Args:
            path(Path): local path to sync
            built_packages(Iterable[Package]): list of packages which has just been built

        Raises:
            SyncFailed: in case of any synchronization unmatched exception
        """
        try:
            self.sync(path, built_packages)
        except Exception:
            self.logger.exception("remote sync failed")
            raise SynchronizationError()

    def sync(self, path: Path, built_packages: Iterable[Package]) -> None:
        """
        sync data to remote server

        Args:
            path(Path): local path to sync
            built_packages(Iterable[Package]): list of packages which has just been built
        """
