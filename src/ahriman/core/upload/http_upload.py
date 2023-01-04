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
import hashlib
import requests

from pathlib import Path
from typing import Any, Dict

from ahriman.core.configuration import Configuration
from ahriman.core.upload.upload import Upload
from ahriman.core.util import exception_response_text


class HttpUpload(Upload):
    """
    helper for the http based uploads

    Attributes:
        auth(Optional[Tuple[str, str]]): HTTP auth object if set
        timeout(int): HTTP request timeout in seconds
    """

    def __init__(self, architecture: str, configuration: Configuration, section: str) -> None:
        """
        default constructor

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            section(str): configuration section name
        """
        Upload.__init__(self, architecture, configuration)
        password = configuration.get(section, "password", fallback=None)
        username = configuration.get(section, "username", fallback=None)
        self.auth = (password, username) if password and username else None
        self.timeout = configuration.getint(section, "timeout", fallback=30)

    @staticmethod
    def calculate_hash(path: Path) -> str:
        """
        calculate file checksum

        Args:
            path(Path): path to local file

        Returns:
            str: calculated checksum of the file
        """
        with path.open("rb") as local_file:
            md5 = hashlib.md5(local_file.read())  # nosec
            return md5.hexdigest()

    @staticmethod
    def get_body(local_files: Dict[Path, str]) -> str:
        """
        generate release body from the checksums as returned from HttpUpload.get_hashes method

        Args:
            local_files(Dict[Path, str]): map of the paths to its checksum

        Returns:
            str: body to be inserted into release
        """
        return "\n".join(f"{file.name} {md5}" for file, md5 in sorted(local_files.items()))

    @staticmethod
    def get_hashes(body: str) -> Dict[str, str]:
        """
        get checksums of the content from the repository

        Args:
            body(str): release string body object

        Returns:
            Dict[str, str]: map of the filename to its checksum as it is written in body
        """
        files = {}
        for line in body.splitlines():
            file, md5 = line.split()
            files[file] = md5
        return files

    def _request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        """
        request wrapper

        Args:
            method(str): request method
            url(str): request url
            **kwargs(Any): request parameters to be passed as is

        Returns:
            requests.Response: request response object
        """
        try:
            response = requests.request(method, url, auth=self.auth, timeout=self.timeout, **kwargs)
            response.raise_for_status()
        except requests.HTTPError as e:
            self.logger.exception("could not perform %s request to %s: %s", method, url, exception_response_text(e))
            raise
        return response
