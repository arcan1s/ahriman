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
import os
import shutil

from email.utils import parsedate_to_datetime
from pathlib import Path
from pyalpm import DB  # type: ignore[import-not-found]
from urllib.parse import urlparse

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import PacmanError
from ahriman.core.http import SyncHttpClient


class PacmanDatabase(SyncHttpClient):
    """
    implementation for database sync, because pyalpm is not always enough

    Attributes:
        LAST_MODIFIED_HEADER(str): last modified header name
        database(DB): pyalpm database object
        repository_paths(RepositoryPaths): repository paths instance
        sync_files_database(bool): sync files database
    """

    LAST_MODIFIED_HEADER = "Last-Modified"

    def __init__(self, database: DB, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            database(DB): pyalpm database object
            configuration(Configuration): configuration instance
        """
        SyncHttpClient.__init__(self)
        self.timeout = None  # reset timeout

        self.database = database
        self.repository_paths = configuration.repository_paths

        self.sync_files_database = configuration.getboolean("alpm", "sync_files_database")

    @staticmethod
    def copy(remote_path: Path, local_path: Path) -> None:
        """
        copy local database file

        Args:
            remote_path(Path): path to source (remote) file
            local_path(Path): path to locally stored file
        """
        shutil.copy(remote_path, local_path)

    def download(self, url: str, local_path: Path) -> None:
        """
        download remote file and store it to local path with the correct last modified headers

        Args:
            url(str): remote url to request file
            local_path(Path): path to locally stored file

        Raises:
            PacmanError: in case if no last-modified header was found
        """
        response = self.make_request("GET", url, stream=True)
        if self.LAST_MODIFIED_HEADER not in response.headers:
            raise PacmanError("No last-modified header found")

        with local_path.open("wb") as local_file:
            for chunk in response.iter_content(chunk_size=1024):
                local_file.write(chunk)

        # set correct (a,m)time for the file
        remote_changed = parsedate_to_datetime(response.headers[self.LAST_MODIFIED_HEADER]).timestamp()
        os.utime(local_path, (remote_changed, remote_changed))

    def is_outdated(self, url: str, local_path: Path) -> bool:
        """
        check if local file is outdated

        Args:
            url(str): remote url to request last modified header
            local_path(Path): path to locally stored file

        Returns:
            bool: True in case if remote file is newer than local file

        Raises:
            PacmanError: in case if no last-modified header was found
        """
        if not local_path.is_file():
            return True  # no local file found, requires to update

        response = self.make_request("HEAD", url)
        if self.LAST_MODIFIED_HEADER not in response.headers:
            raise PacmanError("No last-modified header found")

        remote_changed = parsedate_to_datetime(response.headers["Last-Modified"]).timestamp()
        local_changed = local_path.stat().st_mtime

        return remote_changed > local_changed

    def sync(self, *, force: bool) -> None:
        """
        sync packages and files databases

        Args:
            force(bool): force database synchronization (same as ``pacman -Syy``)
        """
        try:
            self.sync_packages(force=force)
            if self.sync_files_database:
                self.sync_files(force=force)
        except Exception:
            self.logger.exception("exception during update %s", self.database.name)

    def sync_files(self, *, force: bool) -> None:
        """
        sync files by using http request

        Args:
            force(bool): force database synchronization (same as ``pacman -Syy``)
        """
        server = next(iter(self.database.servers))
        filename = f"{self.database.name}.files.tar.gz"
        url = f"{server}/{filename}"

        remote_uri = urlparse(url)
        local_path = Path(self.repository_paths.pacman / "sync" / filename)

        match remote_uri.scheme:
            case "http" | "https":
                if not force and not self.is_outdated(url, local_path):
                    return

                self.download(url, local_path)

            case "file":
                # just copy file as it is relatively cheap operation, no need to check timestamps
                self.copy(Path(remote_uri.path), local_path)

            case other:
                raise PacmanError(f"Unknown or unsupported URL scheme {other}")

    def sync_packages(self, *, force: bool) -> None:
        """
        sync packages by using built-in pyalpm methods

        Args:
            force(bool): force database synchronization (same as ``pacman -Syy``)
        """
        self.database.update(force)
