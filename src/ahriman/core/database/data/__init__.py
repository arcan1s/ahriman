#
# Copyright (c) 2021-2023 ahriman team.
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
from sqlite3 import Connection

from ahriman.core.configuration import Configuration
from ahriman.core.database.data.package_remotes import migrate_package_remotes
from ahriman.core.database.data.package_statuses import migrate_package_statuses
from ahriman.core.database.data.patches import migrate_patches
from ahriman.core.database.data.users import migrate_users_data
from ahriman.models.migration_result import MigrationResult


def migrate_data(result: MigrationResult, connection: Connection, configuration: Configuration) -> None:
    """
    perform data migration

    Args:
        result(MigrationResult): result of the schema migration
        connection(Connection): database connection
        configuration(Configuration): configuration instance
    """
    # initial data migration
    repository_paths = configuration.repository_paths

    if result.old_version <= 0:
        migrate_package_statuses(connection, repository_paths)
        migrate_patches(connection, repository_paths)
        migrate_users_data(connection, configuration)
    if result.old_version <= 1:
        migrate_package_remotes(connection, repository_paths)
