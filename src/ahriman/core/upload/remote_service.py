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
import requests

from functools import cached_property
from pathlib import Path

from ahriman.core.configuration import Configuration
from ahriman.core.http import MultipartType
from ahriman.core.sign.gpg import GPG
from ahriman.core.status.web_client import WebClient
from ahriman.core.upload.http_upload import HttpUpload
from ahriman.core.upload.upload import Upload
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId


class RemoteService(Upload, HttpUpload):
    """
    upload files to another server instance

    Attributes:
        client(WebClient): web client instance
    """

    def __init__(self, repository_id: RepositoryId, configuration: Configuration, section: str) -> None:
        """
        default constructor

        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            section(str): settings section name
        """
        Upload.__init__(self, repository_id, configuration)
        HttpUpload.__init__(self, configuration, section)
        self.client = WebClient(configuration)

    @cached_property
    def session(self) -> requests.Session:
        """
        get or create session

        Returns:
            request.Session: created session object
        """
        return self.client.session

    def package_upload(self, path: Path, package: Package) -> None:
        """
        upload single package to remote

        Args:
            path(Path): local path to sync
            package(Package): package to upload
        """
        def upload(package_path: Path, signature_path: Path | None) -> None:
            files: dict[str, MultipartType] = {}

            try:
                # package part always persists
                files["package"] = package_path.name, package_path.open("rb"), "application/octet-stream", {}
                # signature part is optional
                if signature_path is not None:
                    files["signature"] = signature_path.name, signature_path.open("rb"), "application/octet-stream", {}

                self.make_request("POST", f"{self.client.address}/api/v1/service/upload", files=files)
            finally:
                for _, fd, _, _ in files.values():
                    fd.close()

        for key, descriptor in package.packages.items():
            if descriptor.filename is None:
                self.logger.warning("package %s of %s doesn't have filename set", key, package.base)
                continue

            archive = path / descriptor.filename
            maybe_signature_path = GPG.signature(archive)
            signature = maybe_signature_path if maybe_signature_path.is_file() else None

            upload(archive, signature)

    def sync(self, path: Path, built_packages: list[Package]) -> None:
        """
        sync data to remote server

        Args:
            path(Path): local path to sync
            built_packages(list[Package]): list of packages which has just been built
        """
        for package in built_packages:
            self.package_upload(path, package)
