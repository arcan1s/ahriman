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
from pathlib import Path
from typing import IO

from ahriman.core.configuration import Configuration
from ahriman.core.status.web_client import WebClient
from ahriman.core.upload.upload import Upload
from ahriman.models.package import Package


class RemoteService(Upload):
    """
    upload files to another server instance

    Attributes:
        client(WebClient): web client instance
    """

    def __init__(self, architecture: str, configuration: Configuration, section: str) -> None:
        """
        default constructor

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            section(str): settings section name
        """
        Upload.__init__(self, architecture, configuration)
        del section

        self.client = WebClient(configuration)

    def package_upload(self, path: Path, package: Package) -> None:
        """
        upload single package to remote

        Args:
            path(Path): local path to sync
            package(Package): package to upload
        """
        for key, descriptor in package.packages.items():
            if descriptor.filename is None:
                self.logger.warning("package %s of %s doesn't have filename set", key, package.base)
                continue

            with (path / descriptor.filename).open("rb") as archive:
                # filename, file, content-type, headers
                part: tuple[str, IO[bytes], str, dict[str, str]] = (
                    descriptor.filename, archive, "application/octet-stream", {}
                )
                self.client.make_request("POST", "/api/v1/service/upload", files={"archive": part})

    def sync(self, path: Path, built_packages: list[Package]) -> None:
        """
        sync data to remote server

        Args:
            path(Path): local path to sync
            built_packages(list[Package]): list of packages which has just been built
        """
        for package in built_packages:
            self.package_upload(path, package)
