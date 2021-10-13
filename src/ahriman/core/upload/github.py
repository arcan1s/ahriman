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
import hashlib
import mimetypes
import requests

from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from ahriman.core.configuration import Configuration
from ahriman.core.upload.upload import Upload
from ahriman.core.util import exception_response_text, walk
from ahriman.models.package import Package


class Github(Upload):
    """
    upload files to github releases
    :ivar auth: requests authentication tuple
    :ivar gh_owner: github repository owner
    :ivar gh_repository: github repository name
    """

    def __init__(self, architecture: str, configuration: Configuration) -> None:
        """
        default constructor
        :param architecture: repository architecture
        :param configuration: configuration instance
        """
        Upload.__init__(self, architecture, configuration)
        self.gh_owner = configuration.get("github", "owner")
        self.gh_repository = configuration.get("github", "repository")

        gh_api_key = configuration.get("github", "api_key")
        gh_username = configuration.get("github", "username", fallback=self.gh_owner)
        self.auth = (gh_username, gh_api_key)

    @staticmethod
    def calculate_hash(path: Path) -> str:
        """
        calculate file checksum. Github API does not provide hashes itself, so we have to handle it manually
        :param path: path to local file
        :return: calculated checksum of the file
        """
        with path.open("rb") as local_file:
            md5 = hashlib.md5(local_file.read())  # nosec
            return md5.hexdigest()

    @staticmethod
    def get_body(local_files: Dict[Path, str]) -> str:
        """
        generate release body from the checksums as returned from Github.get_hashes method
        :param local_files: map of the paths to its checksum
        :return: body to be inserted into release
        """
        return "\n".join(f"{file.name} {md5}" for file, md5 in sorted(local_files.items()))

    @staticmethod
    def get_hashes(release: Dict[str, Any]) -> Dict[str, str]:
        """
        get checksums of the content from the repository
        :param release: release object
        :return: map of the filename to its checksum as it is written in body
        """
        body: str = release["body"] or ""
        files = {}
        for line in body.splitlines():
            file, md5 = line.split()
            files[file] = md5
        return files

    def _request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        """
        github request wrapper
        :param method: request method
        :param url: request url
        :param kwargs: request parameters to be passed as is
        :return: request response object
        """
        try:
            response = requests.request(method, url, auth=self.auth, **kwargs)
            response.raise_for_status()
        except requests.HTTPError as e:
            self.logger.exception("could not perform %s request to %s: %s", method, url, exception_response_text(e))
            raise
        return response

    def asset_remove(self, release: Dict[str, Any], name: str) -> None:
        """
        remove asset from the release by name
        :param release: release object
        :param name: asset name
        """
        try:
            asset = next(asset for asset in release["assets"] if asset["name"] == name)
            self._request("DELETE", asset["url"])
        except StopIteration:
            self.logger.info("no asset %s found in release %s", name, release["name"])

    def asset_upload(self, release: Dict[str, Any], path: Path) -> None:
        """
        upload asset to the release
        :param release: release object
        :param path: path to local file
        """
        exists = any(path.name == asset["name"] for asset in release["assets"])
        if exists:
            self.asset_remove(release, path.name)
        (url, _) = release["upload_url"].split("{")  # it is parametrized url
        (mime, _) = mimetypes.guess_type(path)
        headers = {"Content-Type": mime} if mime is not None else {"Content-Type": "application/octet-stream"}
        self._request("POST", url, params={"name": path.name}, data=path.open("rb"), headers=headers)

    def get_local_files(self, path: Path) -> Dict[Path, str]:
        """
        get all local files and their calculated checksums
        :param path: local path to sync
        :return: map of path objects to its checksum
        """
        return {
            local_file: self.calculate_hash(local_file)
            for local_file in walk(path)
        }

    def files_remove(self, release: Dict[str, Any], local_files: Dict[Path, str], remote_files: Dict[str, str]) -> None:
        """
        remove files from github
        :param release: release object
        :param local_files: map of local file paths to its checksum
        :param remote_files: map of the remote files and its checksum
        """
        local_filenames = {local_file.name for local_file in local_files}
        for remote_file in remote_files:
            if remote_file in local_filenames:
                continue
            self.asset_remove(release, remote_file)

    def files_upload(self, release: Dict[str, Any], local_files: Dict[Path, str], remote_files: Dict[str, str]) -> None:
        """
        upload files to github
        :param release: release object
        :param local_files: map of local file paths to its checksum
        :param remote_files: map of the remote files and its checksum
        """
        for local_file, checksum in local_files.items():
            remote_checksum = remote_files.get(local_file.name)
            if remote_checksum == checksum:
                continue
            self.asset_upload(release, local_file)

    def release_create(self) -> Dict[str, Any]:
        """
        create empty release
        :return: github API release object for the new release
        """
        response = self._request("POST", f"https://api.github.com/repos/{self.gh_owner}/{self.gh_repository}/releases",
                                 json={"tag_name": self.architecture, "name": self.architecture})
        release: Dict[str, Any] = response.json()
        return release

    def release_get(self) -> Optional[Dict[str, Any]]:
        """
        get release object if any
        :return: github API release object if release found and None otherwise
        """
        try:
            response = self._request(
                "GET",
                f"https://api.github.com/repos/{self.gh_owner}/{self.gh_repository}/releases/tags/{self.architecture}")
            release: Dict[str, Any] = response.json()
            return release
        except requests.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else None
            if status_code == 404:
                return None
            raise

    def release_update(self, release: Dict[str, Any], body: str) -> None:
        """
        update release
        :param release: release object
        :param body: new release body
        """
        self._request("POST", release["url"], json={"body": body})

    def sync(self, path: Path, built_packages: Iterable[Package]) -> None:
        """
        sync data to remote server
        :param path: local path to sync
        :param built_packages: list of packages which has just been built
        """
        release = self.release_get()
        if release is None:
            release = self.release_create()

        remote_files = self.get_hashes(release)
        local_files = self.get_local_files(path)

        self.files_upload(release, local_files, remote_files)
        self.files_remove(release, local_files, remote_files)
        self.release_update(release, self.get_body(local_files))
