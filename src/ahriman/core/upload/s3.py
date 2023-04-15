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
import boto3  # type: ignore[import]
import hashlib
import mimetypes

from pathlib import Path
from typing import Any

from ahriman.core.configuration import Configuration
from ahriman.core.upload.upload import Upload
from ahriman.core.util import walk
from ahriman.models.package import Package


class S3(Upload):
    """
    boto3 wrapper

    Attributes
        bucket(Any): boto3 S3 bucket object
        chunk_size(int): chunk size for calculating checksums
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
        self.bucket = self.get_bucket(configuration, section)
        self.chunk_size = configuration.getint(section, "chunk_size", fallback=8 * 1024 * 1024)

    @staticmethod
    def calculate_etag(path: Path, chunk_size: int) -> str:
        """
        calculate amazon s3 etag
        credits to https://teppen.io/2018/10/23/aws_s3_verify_etags/
        For this method we have to define nosec because it is out of any security context and provided by AWS

        Args:
            path(Path): path to local file
            chunk_size(int): read chunk size, which depends on client settings

        Returns:
            str: calculated entity tag for local file
        """
        md5s = []
        with path.open("rb") as local_file:
            for chunk in iter(lambda: local_file.read(chunk_size), b""):
                md5s.append(hashlib.md5(chunk))  # nosec

        # in case if there is only one chunk it must be just this checksum
        # and checksum of joined digest otherwise (including empty list)
        checksum = md5s[0] if len(md5s) == 1 else hashlib.md5(b"".join(md5.digest() for md5 in md5s))  # nosec
        # in case if there are more than one chunk it should be appended with amount of chunks
        suffix = f"-{len(md5s)}" if len(md5s) > 1 else ""
        return f"{checksum.hexdigest()}{suffix}"

    @staticmethod
    def get_bucket(configuration: Configuration, section: str) -> Any:
        """
        create resource client from configuration

        Args:
            configuration(Configuration): configuration instance
            section(str): settings section name

        Returns:
            Any: amazon client
        """
        client = boto3.resource(service_name="s3",
                                region_name=configuration.get(section, "region"),
                                aws_access_key_id=configuration.get(section, "access_key"),
                                aws_secret_access_key=configuration.get(section, "secret_key"))
        return client.Bucket(configuration.get(section, "bucket"))

    @staticmethod
    def files_remove(local_files: dict[Path, str], remote_objects: dict[Path, Any]) -> None:
        """
        remove files which have been removed locally

        Args:
            local_files(dict[Path, str]): map of local path object to its checksum
            remote_objects(dict[Path, Any]): map of remote path object to the remote s3 object
        """
        for local_file, remote_object in remote_objects.items():
            if local_file in local_files:
                continue
            remote_object.delete()

    def files_upload(self, path: Path, local_files: dict[Path, str], remote_objects: dict[Path, Any]) -> None:
        """
        upload changed files to s3

        Args:
            path(Path): local path to sync
            local_files(dict[Path, str]): map of local path object to its checksum
            remote_objects(dict[Path, Any]): map of remote path object to the remote s3 object
        """
        for local_file, checksum in local_files.items():
            remote_object = remote_objects.get(local_file)
            # 0 and -1 elements are " (double quote)
            remote_checksum = remote_object.e_tag[1:-1] if remote_object is not None else None
            if remote_checksum == checksum:
                continue

            local_path = path / local_file
            remote_path = Path(self.architecture) / local_file
            (mime, _) = mimetypes.guess_type(local_path)
            extra_args = {"ContentType": mime} if mime is not None else None

            self.bucket.upload_file(Filename=str(local_path), Key=str(remote_path), ExtraArgs=extra_args)

    def get_local_files(self, path: Path) -> dict[Path, str]:
        """
        get all local files and their calculated checksums

        Args:
            path(Path): local path to sync

        Returns:
            dict[Path, str]: map of path object to its checksum
        """
        return {
            local_file.relative_to(path): self.calculate_etag(local_file, self.chunk_size)
            for local_file in walk(path)
        }

    def get_remote_objects(self) -> dict[Path, Any]:
        """
        get all remote objects and their checksums

        Returns:
            dict[Path, Any]: map of path object to the remote s3 object
        """
        objects = self.bucket.objects.filter(Prefix=self.architecture)
        return {Path(item.key).relative_to(self.architecture): item for item in objects}

    def sync(self, path: Path, built_packages: list[Package]) -> None:
        """
        sync data to remote server

        Args:
            path(Path): local path to sync
            built_packages(list[Package]): list of packages which has just been built
        """
        remote_objects = self.get_remote_objects()
        local_files = self.get_local_files(path)

        self.files_upload(path, local_files, remote_objects)
        self.files_remove(local_files, remote_objects)
