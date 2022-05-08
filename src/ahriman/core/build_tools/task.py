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
import logging

from pathlib import Path
from typing import List

from ahriman.core.build_tools.sources import Sources
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import BuildFailed
from ahriman.core.util import check_output
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


class Task:
    """
    base package build task

    Attributes:
        build_logger(logging.Logger): logger for build process
        logger(logging.Logger): class logger
        package(Package): package definitions
        paths(RepositoryPaths): repository paths instance
        uid(int): uid of the repository owner user
    """

    _check_output = check_output

    def __init__(self, package: Package, configuration: Configuration, paths: RepositoryPaths) -> None:
        """
        default constructor

        Args:
            package(Package): package definitions
            configuration(Configuration): configuration instance
            paths(RepositoryPaths): repository paths instance
        """
        self.logger = logging.getLogger("root")
        self.build_logger = logging.getLogger("build_details")
        self.package = package
        self.paths = paths
        self.uid, _ = paths.root_owner

        self.archbuild_flags = configuration.getlist("build", "archbuild_flags", fallback=[])
        self.build_command = configuration.get("build", "build_command")
        self.makepkg_flags = configuration.getlist("build", "makepkg_flags", fallback=[])
        self.makechrootpkg_flags = configuration.getlist("build", "makechrootpkg_flags", fallback=[])

    def build(self, sources_dir: Path) -> List[Path]:
        """
        run package build

        Args:
            sources_dir(Path): path to where sources are

        Returns:
            List[Path]: paths of produced packages
        """
        command = [self.build_command, "-r", str(self.paths.chroot)]
        command.extend(self.archbuild_flags)
        command.extend(["--"] + self.makechrootpkg_flags)
        command.extend(["--"] + self.makepkg_flags)
        self.logger.info("using %s for %s", command, self.package.base)

        Task._check_output(
            *command,
            exception=BuildFailed(self.package.base),
            cwd=sources_dir,
            logger=self.build_logger,
            user=self.uid)

        # well it is not actually correct, but we can deal with it
        packages = Task._check_output("makepkg", "--packagelist",
                                      exception=BuildFailed(self.package.base),
                                      cwd=sources_dir,
                                      logger=self.build_logger).splitlines()
        return [Path(package) for package in packages]

    def init(self, sources_dir: Path, database: SQLite) -> None:
        """
        fetch package from git

        Args:
            sources_dir(Path): local path to fetch
            database(SQLite): database instance
        """
        Sources.load(sources_dir, self.package, database.patches_get(self.package.base), self.paths)
