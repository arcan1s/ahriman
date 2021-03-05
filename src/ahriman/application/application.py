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
import os

from typing import List

from ahriman.core.build_tools.task import Task
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.models.package import Package


class Application:

    def __init__(self, config: Configuration) -> None:
        self.config = config
        self.repository = Repository(config)

    def add(self, names: List[str]) -> None:
        for name in names:
            package = Package.load(name, self.config.get('aur', 'url'))
            task = Task(package, self.config, self.repository.paths)
            task.fetch(os.path.join(self.repository.paths.manual, package.name))

    def remove(self, names: List[str]) -> None:
        self.repository.process_remove(names)

    def sync(self) -> None:
        self.repository.process_sync()

    def update(self, sync: bool) -> None:
        updates = self.repository.updates()
        packages = self.repository.process_build(updates)
        self.repository.process_update(packages)
        if sync:
            self.sync()