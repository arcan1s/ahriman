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
import logging

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.repo import Repo
from ahriman.core.configuration import Configuration
from ahriman.core.database.sqlite import SQLite
from ahriman.core.exceptions import UnsafeRun
from ahriman.core.sign.gpg import GPG
from ahriman.core.status.client import Client
from ahriman.core.util import check_user


class RepositoryProperties:
    """
    repository internal objects holder

    Attributes:
        architecture(str): repository architecture
        configuration(Configuration): configuration instance
        database(SQLite): database instance
        ignore_list(List[str]): package bases which will be ignored during auto updates
        logger(logging.Logger): class logger
        name(str): repository name
        pacman(Pacman): alpm wrapper instance
        paths(RepositoryPaths): repository paths instance
        repo(Repo): repo commands wrapper instance
        reporter(Client): build status reporter instance
        sign(GPG): GPG wrapper instance
    """

    def __init__(self, architecture: str, configuration: Configuration, database: SQLite,
                 no_report: bool, unsafe: bool) -> None:
        """
        default constructor

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            database(SQLite): database instance
            no_report(bool): force disable reporting
            unsafe(bool): if set no user check will be performed before path creation
        """
        self.logger = logging.getLogger("root")
        self.architecture = architecture
        self.configuration = configuration
        self.database = database

        self.name = configuration.get("repository", "name")

        self.paths = configuration.repository_paths
        try:
            check_user(self.paths, unsafe)
            self.paths.tree_create()
        except UnsafeRun:
            self.logger.warning("root owner differs from the current user, skipping tree creation")

        self.ignore_list = configuration.getlist("build", "ignore_packages", fallback=[])
        self.pacman = Pacman(configuration)
        self.sign = GPG(architecture, configuration)
        self.repo = Repo(self.name, self.paths, self.sign.repository_sign_args)
        self.reporter = Client() if no_report else Client.load(configuration)
