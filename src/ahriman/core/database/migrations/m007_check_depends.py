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
from sqlite3 import Connection

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.configuration import Configuration
from ahriman.core.utils import package_like
from ahriman.models.package import Package
from ahriman.models.pacman_synchronization import PacmanSynchronization


__all__ = ["migrate_data", "steps"]


steps = [
    """
    alter table packages add column check_depends json
    """,
]


def migrate_data(connection: Connection, configuration: Configuration) -> None:
    """
    perform data migration

    Args:
        connection(Connection): database connection
        configuration(Configuration): configuration instance
    """
    migrate_package_check_depends(connection, configuration)


def migrate_package_check_depends(connection: Connection, configuration: Configuration) -> None:
    """
    migrate package check depends fields

    Args:
        connection(Connection): database connection
        configuration(Configuration): configuration instance
    """
    if not configuration.repository_paths.repository.is_dir():
        return

    _, repository_id = configuration.check_loaded()
    pacman = Pacman(repository_id, configuration, refresh_database=PacmanSynchronization.Disabled)

    package_list = []
    for full_path in filter(package_like, configuration.repository_paths.repository.iterdir()):
        base = Package.from_archive(full_path, pacman)
        for package, description in base.packages.items():
            package_list.append({
                "check_depends": description.check_depends,
                "package": package,
            })

    connection.executemany(
        """
        update packages set
        check_depends = :check_depends
        where package = :package
        """,
        package_list
    )
