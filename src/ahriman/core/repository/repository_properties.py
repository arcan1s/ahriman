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
from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.repo import Repo
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.log import LazyLogging
from ahriman.core.sign.gpg import GPG
from ahriman.core.status.client import Client
from ahriman.core.triggers import TriggerLoader
from ahriman.models.packagers import Packagers
from ahriman.models.pacman_synchronization import PacmanSynchronization
from ahriman.models.repository_id import RepositoryId
from ahriman.models.repository_paths import RepositoryPaths
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


class RepositoryProperties(LazyLogging):
    """
    repository internal objects holder

    Attributes:
        configuration(Configuration): configuration instance
        database(SQLite): database instance
        ignore_list(list[str]): package bases which will be ignored during auto updates
        pacman(Pacman): alpm wrapper instance
        paths(RepositoryPaths): repository paths instance
        repo(Repo): repo commands wrapper instance
        reporter(Client): build status reporter instance
        repository_id(RepositoryId): repository unique identifier
        sign(GPG): GPG wrapper instance
        triggers(TriggerLoader): triggers holder
        vcs_allowed_age(int): maximal age of the VCS packages before they will be checked
    """

    def __init__(self, repository_id: RepositoryId, configuration: Configuration, database: SQLite, *, report: bool,
                 refresh_pacman_database: PacmanSynchronization) -> None:
        """
        default constructor

        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            database(SQLite): database instance
            report(bool): force enable or disable reporting
            refresh_pacman_database(PacmanSynchronization): pacman database synchronization level
        """
        self.repository_id = repository_id
        self.configuration = configuration
        self.database = database

        self.vcs_allowed_age = configuration.getint("build", "vcs_allowed_age", fallback=0)

        self.paths: RepositoryPaths = configuration.repository_paths  # additional workaround for pycharm typing

        self.ignore_list = configuration.getlist("build", "ignore_packages", fallback=[])
        self.pacman = Pacman(repository_id, configuration, refresh_database=refresh_pacman_database)
        self.sign = GPG(configuration)
        self.repo = Repo(self.name, self.paths, self.sign.repository_sign_args)
        self.reporter = Client.load(repository_id, configuration, report=report)
        self.triggers = TriggerLoader.load(repository_id, configuration)

    @property
    def architecture(self) -> str:
        """
        repository architecture for backward compatibility

        Returns:
            str: repository architecture
        """
        return self.repository_id.architecture

    @property
    def name(self) -> str:
        """
        repository name for backward compatibility

        Returns:
            str: repository name
        """
        return self.repository_id.name

    def packager(self, packagers: Packagers, package_base: str) -> User:
        """
        extract packager from configuration having username

        Args:
            packagers(Packagers): packagers override holder
            package_base(str): package base to lookup

        Returns:
            User | None: user found in database if any and empty object otherwise
        """
        username = packagers.for_base(package_base)
        if username is None:  # none to search
            return User(username="", password="", access=UserAccess.Read, packager_id=None, key=None)  # nosec

        if (user := self.database.user_get(username)) is not None:  # found user
            return user
        # empty user with the username
        return User(username=username, password="", access=UserAccess.Read, packager_id=None, key=None)  # nosec
