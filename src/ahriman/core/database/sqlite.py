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
from __future__ import annotations

import json
import sqlite3

from pathlib import Path
from typing import Type

from ahriman.core.configuration import Configuration
from ahriman.core.database.migrations import Migrations
from ahriman.core.database.operations import AuthOperations, BuildOperations, LogsOperations, PackageOperations, \
    PatchOperations


class SQLite(AuthOperations, BuildOperations, LogsOperations, PackageOperations, PatchOperations):
    """
    wrapper for sqlite3 database

    Examples:
        Database wrapper must be used together with migration and SQLite3 setup. In order to perform it there is
        ``load`` class method::

            >>> from ahriman.core.configuration import Configuration
            >>>
            >>> configuration = Configuration()
            >>> database = SQLite.load(configuration)
            >>> packages = database.packages_get()
    """

    @classmethod
    def load(cls: Type[SQLite], configuration: Configuration) -> SQLite:
        """
        construct instance from configuration

        Args:
            configuration(Configuration): configuration instance

        Returns:
            SQLite: fully initialized instance of the database
        """
        path = cls.database_path(configuration)
        database = cls(path)
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

        self.with_connection(lambda connection: Migrations.migrate(connection, configuration))
        paths.chown(self.path)
