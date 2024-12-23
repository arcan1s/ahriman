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
import hashlib

from pathlib import Path

from ahriman.core.http import SyncHttpClient


class HttpUpload(SyncHttpClient):
    """
    helper for the http based uploads
    """

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
    def get_body(local_files: dict[Path, str]) -> str:
        """
        generate release body from the checksums as returned from HttpUpload.get_hashes method

        Args:
            local_files(dict[Path, str]): map of the paths to its checksum

        Returns:
            str: body to be inserted into release
        """
        return "\n".join(f"{file.name} {md5}" for file, md5 in sorted(local_files.items()))

    @staticmethod
    def get_hashes(body: str) -> dict[str, str]:
        """
        get checksums of the content from the repository

        Args:
            body(str): release string body object

        Returns:
            dict[str, str]: map of the filename to its checksum as it is written in body
        """
        files = {}
        for line in body.splitlines():
            file, md5 = line.split()
            files[file] = md5
        return files
