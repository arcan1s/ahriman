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
import boto3  # type: ignore
import hashlib
import mimetypes

from pathlib import Path
from typing import Any, Dict, Generator, Iterable

from ahriman.core.configuration import Configuration
from ahriman.core.upload.upload import Upload
from ahriman.models.package import Package


class S3(Upload):
    """
    aws-cli wrapper
    :ivar bucket: boto3 S3 bucket object
    :ivar chunk_size: chunk size for calculating checksums
    """

    def __init__(self, architecture: str, configuration: Configuration) -> None:
        """
        default constructor
        :param architecture: repository architecture
        :param configuration: configuration instance
        """
        Upload.__init__(self, architecture, configuration)
        self.bucket = self.get_bucket(configuration)
        self.chunk_size = configuration.getint("s3", "chunk_size", fallback=8 * 1024 * 1024)

    @staticmethod
    def calculate_etag(path: Path, chunk_size: int) -> str:
        """
        calculate amazon s3 etag
        credits to https://teppen.io/2018/10/23/aws_s3_verify_etags/
        For this method we have to define nosec because it is out of any security context and provided by AWS
        :param path: path to local file
        :param chunk_size: read chunk size, which depends on client settings
        :return: calculated entity tag for local file
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
    def get_bucket(configuration: Configuration) -> Any:
        """
        create resource client from configuration
        :param configuration: configuration instance
        :return: amazon client
        """
        client = boto3.resource(service_name="s3",
                                region_name=configuration.get("s3", "region"),
                                aws_access_key_id=configuration.get("s3", "access_key"),
                                aws_secret_access_key=configuration.get("s3", "secret_key"))
        return client.Bucket(configuration.get("s3", "bucket"))

    def get_local_files(self, path: Path) -> Dict[Path, str]:
        """
        get all local files and their calculated checksums
        :param path: local path to sync
        :return: map of path object to its checksum
        """
        # credits to https://stackoverflow.com/a/64915960
        def walk(directory_path: Path) -> Generator[Path, None, None]:
            for element in directory_path.iterdir():
                if element.is_dir():
                    yield from walk(element)
                    continue
                yield element
        return {
            local_file.relative_to(path): self.calculate_etag(local_file, self.chunk_size)
            for local_file in walk(path)
        }

    def get_remote_objects(self) -> Dict[Path, Any]:
        """
        get all remote objects and their checksums
        :return: map of path object to the remote s3 object
        """
        objects = self.bucket.objects.filter(Prefix=self.architecture)
        return {Path(item.key).relative_to(self.architecture): item for item in objects}

    def sync(self, path: Path, built_packages: Iterable[Package]) -> None:
        """
        sync data to remote server
        :param path: local path to sync
        :param built_packages: list of packages which has just been built
        """
        remote_objects = self.get_remote_objects()
        local_files = self.get_local_files(path)

        # sync to remotes first
        for local_file, checksum in local_files.items():
            remote_object = remote_objects.get(local_file)
            # 0 and -1 elements are " (double quote)
            remote_checksum = remote_object.e_tag[1:-1] if remote_object is not None else None
            if remote_checksum == checksum:
                continue

            local_path = path / local_file
            remote_path = Path(self.architecture) / local_file
            (mime, _) = mimetypes.guess_type(local_path)
            extra_args = {"Content-Type": mime} if mime is not None else None

            self.bucket.upload_file(Filename=str(local_path), Key=str(remote_path), ExtraArgs=extra_args)

        # remove files which were removed locally
        for local_file, remote_object in remote_objects.items():
            if local_file in local_files:
                continue
            remote_object.delete()
