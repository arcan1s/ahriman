#
# Copyright (c) 2021-2025 ahriman team.
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
from typing import Self

from ahriman.core import _Context, context
from ahriman.core.alpm.pacman import Pacman
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.repository.executor import Executor
from ahriman.core.repository.update_handler import UpdateHandler
from ahriman.core.sign.gpg import GPG
from ahriman.core.status import Client
from ahriman.models.pacman_synchronization import PacmanSynchronization
from ahriman.models.repository_id import RepositoryId


class Repository(Executor, UpdateHandler):
    """
    base repository control class

    Examples:
        This class along with traits provides access to local repository actions, e.g. remove packages, update packages,
        sync local repository to remote, generate report, etc.::

            >>> from ahriman.core.configuration import Configuration
            >>> from ahriman.core.database import SQLite
            >>>
            >>> configuration = Configuration()
            >>> database = SQLite.load(configuration)
            >>> repository = Repository.load(RepositoryId("x86_64", "x86_64"), configuration, database, report=True)
            >>> known_packages = repository.packages()
            >>>
            >>> build_result = repository.process_build(known_packages)
            >>> built_packages = repository.packages_built()
            >>> update_result = repository.process_update(built_packages)
            >>>
            >>> repository.triggers.on_result(update_result, repository.packages())
    """

    @classmethod
    def load(cls, repository_id: RepositoryId, configuration: Configuration, database: SQLite, *, report: bool,
             refresh_pacman_database: PacmanSynchronization = PacmanSynchronization.Disabled) -> Self:
        """
        load instance from argument list

        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            database(SQLite): database instance
            report(bool): force enable or disable reporting
            refresh_pacman_database(PacmanSynchronization, optional): pacman database synchronization level
                (Default value = PacmanSynchronization.Disabled)

        Returns:
            Self: fully loaded repository class instance
        """
        instance = cls(repository_id, configuration, database,
                       report=report, refresh_pacman_database=refresh_pacman_database)
        instance._set_context()
        return instance

    def _set_context(self) -> None:
        """
        create context variables and set their values
        """
        # there is a reason why do we always create fresh context here.
        # Issue is that if we are going to spawn child process (e.g. from web service), we will use context variables
        # from parent process which we would like to avoid (at least they can have different flags).
        # In the another hand, this class is the entry point of the application, so we will always create context
        # exactly on the start of the application.
        # And, finally, context still provides default not-initialized value, in case if someone would like to use it
        # directly without loader
        ctx = _Context()

        ctx.set(SQLite, self.database)
        ctx.set(Configuration, self.configuration)
        ctx.set(Pacman, self.pacman)
        ctx.set(GPG, self.sign)
        ctx.set(Client, self.reporter)

        ctx.set(type(self), self)

        context.set(ctx)
