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
import argparse

from dataclasses import replace
from sqlite3 import Connection

from ahriman.application.handlers.handler import Handler
from ahriman.core.alpm.pacman import Pacman
from ahriman.core.configuration import Configuration
from ahriman.core.sign.gpg import GPG
from ahriman.core.utils import atomic_move, package_like, symlink_relative
from ahriman.models.package import Package
from ahriman.models.pacman_synchronization import PacmanSynchronization
from ahriman.models.repository_paths import RepositoryPaths


__all__ = ["migrate_data"]


def migrate_data(connection: Connection, configuration: Configuration) -> None:
    """
    perform data migration

    Args:
        connection(Connection): database connection
        configuration(Configuration): configuration instance
    """
    del connection

    config_path, _ = configuration.check_loaded()
    args = argparse.Namespace(configuration=config_path, architecture=None, repository=None, repository_id=None)

    for repository_id in Handler.repositories_extract(args):
        paths = replace(configuration.repository_paths, repository_id=repository_id)
        pacman = Pacman(repository_id, configuration, refresh_database=PacmanSynchronization.Disabled)

        # create archive directory if required
        if not paths.archive.is_dir():
            with paths.preserve_owner():
                paths.archive.mkdir(mode=0o755, parents=True)

        move_packages(paths, pacman)


def move_packages(repository_paths: RepositoryPaths, pacman: Pacman) -> None:
    """
    move packages from repository to archive and create symbolic links

    Args:
        repository_paths(RepositoryPaths): repository paths instance
        pacman(Pacman): alpm wrapper instance
    """
    for archive in filter(package_like, repository_paths.repository.iterdir()):
        if not archive.is_file(follow_symlinks=False):
            continue  # skip symbolic links if any

        package = Package.from_archive(archive, pacman)
        artifacts = [archive]
        # check if there are signatures for this package and append it here too
        if (signature := GPG.signature(archive)).exists():
            artifacts.append(signature)

        for source in artifacts:
            # move package to the archive directory
            target = repository_paths.archive_for(package.base) / source.name
            atomic_move(source, target)
            # create symlink to the archive
            symlink_relative(source, target)
