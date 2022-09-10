#
# Copyright (c) 2021-2022 ahriman team.
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
import mimetypes
import requests

from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from ahriman.core.configuration import Configuration
from ahriman.core.upload.http_upload import HttpUpload
from ahriman.core.util import walk
from ahriman.models.package import Package


class Github(HttpUpload):
    """
    upload files to github releases

    Attributes:
        github_owner(str): github repository owner
        github_repository(str): github repository name
    """

    def __init__(self, architecture: str, configuration: Configuration, section: str) -> None:
        """
        default constructor

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            section(str): settings section name
        """
        HttpUpload.__init__(self, architecture, configuration, section)
        self.github_owner = configuration.get(section, "owner")
        self.github_repository = configuration.get(section, "repository")

    def asset_remove(self, release: Dict[str, Any], name: str) -> None:
        """
        remove asset from the release by name

        Args:
            release(Dict[str, Any]): release object
            name(str): asset name
        """
        try:
            asset = next(asset for asset in release["assets"] if asset["name"] == name)
            self._request("DELETE", asset["url"])
        except StopIteration:
            self.logger.info("no asset %s found in release %s", name, release["name"])

    def asset_upload(self, release: Dict[str, Any], path: Path) -> None:
        """
        upload asset to the release

        Args:
            release(Dict[str, Any]): release object
            path(Path): path to local file
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

        Args:
            path(Path): local path to sync

        Returns:
            Dict[Path, str]: map of path objects to its checksum
        """
        return {
            local_file: self.calculate_hash(local_file)
            for local_file in walk(path)
        }

    def files_remove(self, release: Dict[str, Any], local_files: Dict[Path, str], remote_files: Dict[str, str]) -> None:
        """
        remove files from github

        Args:
            release(Dict[str, Any]): release object
            local_files(Dict[Path, str]): map of local file paths to its checksum
            remote_files(Dict[str, str]): map of the remote files and its checksum
        """
        local_filenames = {local_file.name for local_file in local_files}
        for remote_file in remote_files:
            if remote_file in local_filenames:
                continue
            self.asset_remove(release, remote_file)

    def files_upload(self, release: Dict[str, Any], local_files: Dict[Path, str], remote_files: Dict[str, str]) -> None:
        """
        upload files to github

        Args:
            release(Dict[str, Any]): release object
            local_files(Dict[Path, str]): map of local file paths to its checksum
            remote_files(Dict[str, str]): map of the remote files and its checksum
        """
        for local_file, checksum in local_files.items():
            remote_checksum = remote_files.get(local_file.name)
            if remote_checksum == checksum:
                continue
            self.asset_upload(release, local_file)

    def release_create(self) -> Dict[str, Any]:
        """
        create empty release

        Returns:
            Dict[str, Any]: github API release object for the new release
        """
        url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repository}/releases"
        response = self._request("POST", url, json={"tag_name": self.architecture, "name": self.architecture})
        release: Dict[str, Any] = response.json()
        return release

    def release_get(self) -> Optional[Dict[str, Any]]:
        """
        get release object if any

        Returns:
            Optional[Dict[str, Any]]: github API release object if release found and None otherwise
        """
        url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repository}/releases/tags/{self.architecture}"
        try:
            response = self._request("GET", url)
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

        Args:
            release(Dict[str, Any]): release object
            body(str): new release body
        """
        self._request("POST", release["url"], json={"body": body})

    def sync(self, path: Path, built_packages: Iterable[Package]) -> None:
        """
        sync data to remote server

        Args:
            path(Path): local path to sync
            built_packages(Iterable[Package]): list of packages which has just been built
        """
        release = self.release_get()
        if release is None:
            release = self.release_create()

        body: str = release.get("body") or ""
        remote_files = self.get_hashes(body)
        local_files = self.get_local_files(path)

        self.files_upload(release, local_files, remote_files)
        self.files_remove(release, local_files, remote_files)
        self.release_update(release, self.get_body(local_files))
