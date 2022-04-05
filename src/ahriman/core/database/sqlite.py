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
from sqlite3 import Connection
from typing import Type

from ahriman.core.configuration import Configuration
from ahriman.core.database.data import migrate_data
from ahriman.core.database.migrations import Migrations
from ahriman.core.database.operations.auth_operations import AuthOperations
from ahriman.core.database.operations.build_operations import BuildOperations
from ahriman.core.database.operations.package_operations import PackageOperations
from ahriman.core.database.operations.patch_operations import PatchOperations


class SQLite(AuthOperations, BuildOperations, PackageOperations, PatchOperations):
    """
    wrapper for sqlite3 database
    """

    @classmethod
    def load(cls: Type[SQLite], configuration: Configuration) -> SQLite:
        """
        construct instance from configuration
        :param configuration: configuration instance
        :return: fully initialized instance of the database
        """
        path = cls.database_path(configuration)
        database = cls(path)
        database.init(configuration)
        return database

    @staticmethod
    def database_path(configuration: Configuration) -> Path:
        """
        read database from configuration
        :param configuration: configuration instance
        :return: database path according to the configuration
        """
        return configuration.getpath("settings", "database")

    def init(self, configuration: Configuration) -> None:
        """
        perform database migrations
        :param configuration: configuration instance
        """
        # custom types support
        sqlite3.register_adapter(dict, json.dumps)
        sqlite3.register_adapter(list, json.dumps)
        sqlite3.register_converter("json", json.loads)

        paths = configuration.repository_paths

        def run(connection: Connection) -> None:
            result = Migrations.migrate(connection)
            migrate_data(result, connection, configuration, paths)

        self.with_connection(run)
        paths.chown(self.path)
