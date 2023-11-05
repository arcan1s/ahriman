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

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import SynchronizationError
from ahriman.core.log import LazyLogging
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId
from ahriman.models.upload_settings import UploadSettings


class Upload(LazyLogging):
    """
    base remote sync class

    Attributes:
        configuration(Configuration): configuration instance
        repository_id(RepositoryId): repository unique identifier

    Examples:
        These classes provide the way to upload packages to remote sources as it is described in their implementations.
        Basic flow includes class instantiating by using the :func:`load` method and then calling the :func:`run` method
        which wraps any internal exceptions into the :exc:`ahriman.core.exceptions.SynchronizationError` exception::

            >>> configuration = Configuration()
            >>> upload = Upload.load(RepositoryId("x86_64", "aur-clone"), configuration, "s3")
            >>> upload.run(configuration.repository_paths.repository, [])

        Or in case if direct access to exception is required, the :func:`sync` method can be used::

            >>> try:
            >>>     upload.sync(configuration.repository_paths.repository, [])
            >>> except Exception as ex:
            >>>     handle_exceptions(ex)
    """

    def __init__(self, repository_id: RepositoryId, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
        """
        self.repository_id = repository_id
        self.configuration = configuration

    @staticmethod
    def load(repository_id: RepositoryId, configuration: Configuration, target: str) -> Upload:
        """
        load client from settings

        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            target(str): target to run sync (e.g. s3)

        Returns:
            Upload: client according to current settings
        """
        section, provider_name = configuration.gettype(target, repository_id)
        match UploadSettings.from_option(provider_name):
            case UploadSettings.Rsync:
                from ahriman.core.upload.rsync import Rsync
                return Rsync(repository_id, configuration, section)
            case UploadSettings.S3:
                from ahriman.core.upload.s3 import S3
                return S3(repository_id, configuration, section)
            case UploadSettings.GitHub:
                from ahriman.core.upload.github import GitHub
                return GitHub(repository_id, configuration, section)
            case UploadSettings.RemoteService:
                from ahriman.core.upload.remote_service import RemoteService
                return RemoteService(repository_id, configuration, section)
            case _:
                return Upload(repository_id, configuration)  # should never happen

    def run(self, path: Path, built_packages: list[Package]) -> None:
        """
        run remote sync

        Args:
            path(Path): local path to sync
            built_packages(list[Package]): list of packages which has just been built

        Raises:
            SynchronizationError: in case of any synchronization unmatched exception
        """
        try:
            self.sync(path, built_packages)
        except Exception:
            self.logger.exception("remote sync failed")
            raise SynchronizationError

    def sync(self, path: Path, built_packages: list[Package]) -> None:
        """
        sync data to remote server

        Args:
            path(Path): local path to sync
            built_packages(list[Package]): list of packages which has just been built
        """
