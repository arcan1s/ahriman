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
import argparse
import pwd

from pathlib import Path
from tarfile import TarFile

from ahriman.application.handlers import Handler
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.models.repository_id import RepositoryId


class Backup(Handler):
    """
    backup packages handler
    """

    ALLOW_MULTI_ARCHITECTURE_RUN = False  # system-wide action

    @classmethod
    def run(cls, args: argparse.Namespace, repository_id: RepositoryId, configuration: Configuration, *,
            report: bool) -> None:
        """
        callback for command line

        Args:
            args(argparse.Namespace): command line args
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
        """
        backup_paths = Backup.get_paths(configuration)
        with TarFile(args.path, mode="w") as archive:  # well we don't actually use compression
            for backup_path in backup_paths:
                archive.add(backup_path)

    @staticmethod
    def get_paths(configuration: Configuration) -> set[Path]:
        """
        extract paths to back up

        Args:
            configuration(Configuration): configuration instance

        Returns:
            set[Path]: map of the filesystem paths
        """
        paths = set(configuration.include.glob("*.ini"))

        root, _ = configuration.check_loaded()
        paths.add(root)  # the configuration itself
        paths.add(SQLite.database_path(configuration))  # database

        # local caches
        repository_paths = configuration.repository_paths
        if repository_paths.cache.is_dir():
            paths.add(repository_paths.cache)

        # gnupg home with imported keys
        uid, _ = repository_paths.root_owner
        system_user = pwd.getpwuid(uid)
        gnupg_home = Path(system_user.pw_dir) / ".gnupg"
        if gnupg_home.is_dir():
            paths.add(gnupg_home)

        return paths
