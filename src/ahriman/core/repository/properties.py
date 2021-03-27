#
# Copyright (c) 2021 Evgenii Alekseev.
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

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.repo import Repo
from ahriman.core.configuration import Configuration
from ahriman.core.sign.gpg import GPG
from ahriman.core.status.client import Client
from ahriman.models.repository_paths import RepositoryPaths


class Properties:
    """
    repository internal objects holder
    :ivar architecture: repository architecture
    :ivar aur_url: base AUR url
    :ivar config: configuration instance
    :ivar logger: class logger
    :ivar name: repository name
    :ivar pacman: alpm wrapper instance
    :ivar paths: repository paths instance
    :ivar repo: repo commands wrapper instance
    :ivar reporter: build status reporter instance
    :ivar sign: GPG wrapper instance
    """

    def __init__(self, architecture: str, config: Configuration) -> None:
        self.logger = logging.getLogger("builder")
        self.architecture = architecture
        self.config = config

        self.aur_url = config.get("alpm", "aur_url")
        self.name = config.get("repository", "name")

        self.paths = RepositoryPaths(Path(config.get("repository", "root")), architecture)
        self.paths.create_tree()

        self.pacman = Pacman(config)
        self.sign = GPG(architecture, config)
        self.repo = Repo(self.name, self.paths, self.sign.repository_sign_args)
        self.reporter = Client.load(architecture, config)
