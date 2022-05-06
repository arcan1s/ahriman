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
import argparse
import pwd

from pathlib import Path
from tarfile import TarFile
from typing import Set, Type

from ahriman.application.handlers import Handler
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite


class Backup(Handler):
    """
    backup packages handler
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = False  # it should be called only as "no-architecture"

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str,
            configuration: Configuration, no_report: bool, unsafe: bool) -> None:
        """
        callback for command line

        Args:
            args(argparse.Namespace): command line args
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            no_report(bool): force disable reporting
            unsafe(bool): if set no user check will be performed before path creation
        """
        backup_paths = Backup.get_paths(configuration)
        with TarFile(args.path, mode="w") as archive:  # well we don't actually use compression
            for backup_path in backup_paths:
                archive.add(backup_path)

    @staticmethod
    def get_paths(configuration: Configuration) -> Set[Path]:
        """
        extract paths to backup

        Args:
            configuration(Configuration): configuration instance

        Returns:
            Set[Path]: map of the filesystem paths
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
