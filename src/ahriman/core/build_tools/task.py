#
# Copyright (c) 2021 ahriman team.
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
import shutil

from pathlib import Path
from typing import List, Optional

from ahriman.core.build_tools.sources import Sources
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import BuildFailed
from ahriman.core.util import check_output
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


class Task:
    """
    base package build task
    :ivar build_logger: logger for build process
    :ivar logger: class logger
    :ivar package: package definitions
    :ivar paths: repository paths instance
    """

    _check_output = check_output

    def __init__(self, package: Package, configuration: Configuration, paths: RepositoryPaths) -> None:
        """
        default constructor
        :param package: package definitions
        :param configuration: configuration instance
        :param paths: repository paths instance
        """
        self.logger = logging.getLogger("builder")
        self.build_logger = logging.getLogger("build_details")
        self.package = package
        self.paths = paths

        self.archbuild_flags = configuration.getlist("build", "archbuild_flags", fallback=[])
        self.build_command = configuration.get("build", "build_command")
        self.makepkg_flags = configuration.getlist("build", "makepkg_flags", fallback=[])
        self.makechrootpkg_flags = configuration.getlist("build", "makechrootpkg_flags", fallback=[])

    def build(self) -> List[Path]:
        """
        run package build
        :return: paths of produced packages
        """
        command = [self.build_command, "-r", str(self.paths.chroot)]
        command.extend(self.archbuild_flags)
        command.extend(["--"] + self.makechrootpkg_flags)
        command.extend(["--"] + self.makepkg_flags)
        self.logger.info("using %s for %s", command, self.package.base)

        Task._check_output(
            *command,
            exception=BuildFailed(self.package.base),
            cwd=self.paths.sources_for(self.package.base),
            logger=self.build_logger)

        # well it is not actually correct, but we can deal with it
        packages = Task._check_output("makepkg", "--packagelist",
                                      exception=BuildFailed(self.package.base),
                                      cwd=self.paths.sources_for(self.package.base),
                                      logger=self.build_logger).splitlines()
        return [Path(package) for package in packages]

    def init(self, path: Optional[Path] = None) -> None:
        """
        fetch package from git
        :param path: optional local path to fetch. If not set default path will be used
        """
        git_path = path or self.paths.sources_for(self.package.base)
        if self.paths.cache_for(self.package.base).is_dir():
            # no need to clone whole repository, just copy from cache first
            shutil.copytree(self.paths.cache_for(self.package.base), git_path)
        Sources.load(git_path, self.package.git_url, self.paths.patches_for(self.package.base))
