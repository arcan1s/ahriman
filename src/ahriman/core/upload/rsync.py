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
from pathlib import Path

from ahriman.core.configuration import Configuration
from ahriman.core.upload.upload import Upload
from ahriman.core.util import check_output
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId


class Rsync(Upload):
    """
    rsync wrapper

    Attributes:
        command(list[str]): command arguments for sync
        remote(str): remote address to sync
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
        self.command = configuration.getlist(section, "command")
        self.remote = configuration.get(section, "remote")

    def sync(self, path: Path, built_packages: list[Package]) -> None:
        """
        sync data to remote server

        Args:
            path(Path): local path to sync
            built_packages(list[Package]): list of packages which has just been built
        """
        check_output(*self.command, str(path), self.remote, logger=self.logger)
