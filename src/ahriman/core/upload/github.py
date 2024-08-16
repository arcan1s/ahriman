#
# Copyright (c) 2021-2024 ahriman team.
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
from typing import Any

from ahriman.core.configuration import Configuration
from ahriman.core.upload.http_upload import HttpUpload
from ahriman.core.upload.upload import Upload
from ahriman.core.utils import walk
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId


class GitHub(Upload, HttpUpload):
    """
    upload files to GitHub releases

    Attributes:
        github_owner(str): GitHub repository owner
        github_release_tag(str): GitHub release tag
        github_release_tag_name(str): GitHub release tag name
        github_repository(str): GitHub repository name
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

        self.github_owner = configuration.get(section, "owner")
        self.github_repository = configuration.get(section, "repository")

        if configuration.getboolean(section, "use_full_release_name", fallback=False):
            self.github_release_tag = f"{repository_id.name}-{repository_id.architecture}"
            self.github_release_tag_name = f"{repository_id.name} {repository_id.architecture}"
        else:
            self.github_release_tag_name = self.github_release_tag = repository_id.architecture

    def asset_remove(self, release: dict[str, Any], name: str) -> None:
        """
        remove asset from the release by name

        Args:
            release(dict[str, Any]): release object
            name(str): asset name
        """
        try:
            asset = next(asset for asset in release["assets"] if asset["name"] == name)
            self.make_request("DELETE", asset["url"])
        except StopIteration:
            self.logger.info("no asset %s found in release %s", name, release["name"])

    def asset_upload(self, release: dict[str, Any], path: Path) -> None:
        """
        upload asset to the release

        Args:
            release(dict[str, Any]): release object
            path(Path): path to local file
        """
        exists = any(path.name == asset["name"] for asset in release["assets"])
        if exists:
            self.asset_remove(release, path.name)
        (url, _) = release["upload_url"].split("{")  # it is parametrized url
        (mime, _) = mimetypes.guess_type(path)
        headers = {"Content-Type": mime} if mime is not None else {"Content-Type": "application/octet-stream"}

        with path.open("rb") as archive:
            self.make_request("POST", url, params=[("name", path.name)], data=archive, headers=headers)

    def files_remove(self, release: dict[str, Any], local_files: dict[Path, str], remote_files: dict[str, str]) -> None:
        """
        remove files from GitHub

        Args:
            release(dict[str, Any]): release object
            local_files(dict[Path, str]): map of local file paths to its checksum
            remote_files(dict[str, str]): map of the remote files and its checksum
        """
        local_filenames = {local_file.name for local_file in local_files}
        for remote_file in remote_files:
            if remote_file in local_filenames:
                continue
            self.asset_remove(release, remote_file)

    def files_upload(self, release: dict[str, Any], local_files: dict[Path, str], remote_files: dict[str, str]) -> None:
        """
        upload files to GitHub

        Args:
            release(dict[str, Any]): release object
            local_files(dict[Path, str]): map of local file paths to its checksum
            remote_files(dict[str, str]): map of the remote files and its checksum
        """
        for local_file, checksum in local_files.items():
            remote_checksum = remote_files.get(local_file.name)
            if remote_checksum == checksum:
                continue
            self.asset_upload(release, local_file)

    def get_local_files(self, path: Path) -> dict[Path, str]:
        """
        get all local files and their calculated checksums

        Args:
            path(Path): local path to sync

        Returns:
            dict[Path, str]: map of path objects to its checksum
        """
        return {
            local_file: self.calculate_hash(local_file)
            for local_file in walk(path)
        }

    def release_create(self) -> dict[str, Any]:
        """
        create empty release

        Returns:
            dict[str, Any]: GitHub API release object for the new release
        """
        url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repository}/releases"
        response = self.make_request("POST", url, json={
            "tag_name": self.github_release_tag,
            "name": self.github_release_tag_name,
        })
        release: dict[str, Any] = response.json()
        return release

    def release_get(self) -> dict[str, Any] | None:
        """
        get release object if any

        Returns:
            dict[str, Any] | None: GitHub API release object if release found and None otherwise
        """
        url = f"https://api.github.com/repos/{self.github_owner}/{
            self.github_repository}/releases/tags/{self.github_release_tag}"
        try:
            response = self.make_request("GET", url)
            release: dict[str, Any] = response.json()
            return release
        except requests.HTTPError as ex:
            status_code = ex.response.status_code if ex.response is not None else None
            if status_code == 404:
                return None
            raise

    def release_update(self, release: dict[str, Any], body: str) -> None:
        """
        update release

        Args:
            release(dict[str, Any]): release object
            body(str): new release body
        """
        self.make_request("POST", release["url"], json={"body": body})

    def sync(self, path: Path, built_packages: list[Package]) -> None:
        """
        sync data to remote server

        Args:
            path(Path): local path to sync
            built_packages(list[Package]): list of packages which has just been built
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
