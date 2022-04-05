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
from sqlite3 import Connection

from ahriman.core.configuration import Configuration
from ahriman.core.database.data.package_statuses import migrate_package_statuses
from ahriman.core.database.data.patches import migrate_patches
from ahriman.core.database.data.users import migrate_users_data
from ahriman.models.migration_result import MigrationResult
from ahriman.models.repository_paths import RepositoryPaths


def migrate_data(result: MigrationResult, connection: Connection,
                 configuration: Configuration, paths: RepositoryPaths) -> None:
    """
    perform data migration
    :param result: result of the schema migration
    :param connection: database connection
    :param configuration: configuration instance
    :param paths: repository paths instance
    """
    # initial data migration
    if result.old_version <= 0:
        migrate_package_statuses(connection, paths)
        migrate_patches(connection, paths)
        migrate_users_data(connection, configuration)
