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
import json
import sqlite3

from pathlib import Path
from typing import Self

from ahriman.core.configuration import Configuration
from ahriman.core.database.migrations import Migrations
from ahriman.core.database.operations import AuthOperations, BuildOperations, ChangesOperations, \
    DependenciesOperations, LogsOperations, PackageOperations, PatchOperations


# pylint: disable=too-many-ancestors
class SQLite(
        AuthOperations,
        BuildOperations,
        ChangesOperations,
        DependenciesOperations,
        LogsOperations,
        PackageOperations,
        PatchOperations):
    """
    wrapper for sqlite3 database

    Examples:
        Database wrapper must be used together with migration and SQLite3 setup. In order to perform it there is
        :func:`load()` class method::

            >>> from ahriman.core.configuration import Configuration
            >>>
            >>> configuration = Configuration()
            >>> database = SQLite.load(configuration)
            >>> packages = database.packages_get()
    """

    @classmethod
    def load(cls, configuration: Configuration) -> Self:
        """
        construct instance from configuration

        Args:
            configuration(Configuration): configuration instance

        Returns:
            Self: fully initialized instance of the database
        """
        path = cls.database_path(configuration)
        _, repository_id = configuration.check_loaded()

        database = cls(path, repository_id, configuration.repository_paths)
        database.init(configuration)

        return database

    @staticmethod
    def database_path(configuration: Configuration) -> Path:
        """
        read database from configuration

        Args:
            configuration(Configuration): configuration instance

        Returns:
            Path: database path according to the configuration
        """
        return configuration.getpath("settings", "database")

    def init(self, configuration: Configuration) -> None:
        """
        perform database migrations

        Args:
            configuration(Configuration): configuration instance
        """
        # custom types support
        sqlite3.register_adapter(dict, json.dumps)
        sqlite3.register_adapter(list, json.dumps)
        sqlite3.register_converter("json", json.loads)

        paths = configuration.repository_paths

        if configuration.getboolean("settings", "apply_migrations", fallback=True):
            self.with_connection(lambda connection: Migrations.migrate(connection, configuration))
        paths.chown(self.path)

    def package_clear(self, package_base: str) -> None:
        """
        completely remove package from all tables

        Args:
            package_base(str): package base to remove

        Examples:
            This method completely removes the package from all tables and must be used, e.g. on package removal::

            >>> database.package_clear("ahriman")
        """
        self.build_queue_clear(package_base)
        self.patches_remove(package_base, [])
        self.logs_remove(package_base, None)
        self.changes_remove(package_base)
        self.dependencies_remove(package_base)

        # remove local cache too
        self._repository_paths.tree_clear(package_base)
