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

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.repo import Repo
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import UnsafeRun
from ahriman.core.sign.gpg import GPG
from ahriman.core.status.client import Client
from ahriman.core.util import check_user
from ahriman.models.repository_paths import RepositoryPaths


class Properties:
    """
    repository internal objects holder
    :ivar architecture: repository architecture
    :ivar aur_url: base AUR url
    :ivar configuration: configuration instance
    :ivar ignore_list: package bases which will be ignored during auto updates
    :ivar logger: class logger
    :ivar name: repository name
    :ivar pacman: alpm wrapper instance
    :ivar paths: repository paths instance
    :ivar repo: repo commands wrapper instance
    :ivar reporter: build status reporter instance
    :ivar sign: GPG wrapper instance
    """

    def __init__(self, architecture: str, configuration: Configuration, no_report: bool) -> None:
        """
        default constructor
        :param architecture: repository architecture
        :param configuration: configuration instance
        :param no_report: force disable reporting
        """
        self.logger = logging.getLogger("root")
        self.architecture = architecture
        self.configuration = configuration

        self.aur_url = configuration.get("alpm", "aur_url")
        self.name = configuration.get("repository", "name")

        self.paths = RepositoryPaths(configuration.getpath("repository", "root"), architecture)
        try:
            check_user(self.paths.root)
            self.paths.tree_create()
        except UnsafeRun:
            self.logger.exception("root owner differs from the current user, skipping tree creation")

        self.ignore_list = configuration.getlist("build", "ignore_packages", fallback=[])
        self.pacman = Pacman(configuration)
        self.sign = GPG(architecture, configuration)
        self.repo = Repo(self.name, self.paths, self.sign.repository_sign_args)
        self.reporter = Client() if no_report else Client.load(configuration)
