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
from pathlib import Path
from typing import Iterable

from ahriman.core.configuration import Configuration
from ahriman.core.upload.upload import Upload
from ahriman.core.util import check_output
from ahriman.models.package import Package


class Rsync(Upload):
    """
    rsync wrapper

    Attributes:
        command(List[str]): command arguments for sync
        remote(str): remote address to sync
    """

    _check_output = check_output

    def __init__(self, architecture: str, configuration: Configuration, section: str) -> None:
        """
        default constructor

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            section(str): settings section name
        """
        Upload.__init__(self, architecture, configuration)
        self.command = configuration.getlist(section, "command")
        self.remote = configuration.get(section, "remote")

    def sync(self, path: Path, built_packages: Iterable[Package]) -> None:
        """
        sync data to remote server

        Args:
            path(Path): local path to sync
            built_packages(Iterable[Package]): list of packages which has just been built
        """
        Rsync._check_output(*self.command, str(path), self.remote, logger=self.logger)
