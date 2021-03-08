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
import os
import shutil

from typing import Callable, List, Optional

from ahriman.core.build_tools.task import Task
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.models.package import Package


class Application:

    def __init__(self, architecture: str, config: Configuration) -> None:
        self.logger = logging.getLogger('root')
        self.config = config
        self.architecture = architecture
        self.repository = Repository(architecture, config)

    def _finalize(self) -> None:
        self.report()
        self.sync()

    def get_updates(self, no_aur: bool, no_manual: bool, no_vcs: bool,
                    log_fn: Callable[[str], None]) -> List[Package]:
        updates = []
        checked: List[str] = []

        if not no_aur:
            updates.extend(self.repository.updates_aur(no_vcs, checked))
        if not no_manual:
            updates.extend(self.repository.updates_manual(checked))

        for package in updates:
            log_fn(f'{package.name} = {package.version}')

        return updates

    def add(self, names: List[str]) -> None:
        def add_manual(name: str) -> None:
            package = Package.load(name, self.config.get('aur', 'url'))
            Task.fetch(os.path.join(self.repository.paths.manual, package.name), package.url)

        def add_archive(src: str) -> None:
            dst = os.path.join(self.repository.paths.packages, os.path.basename(src))
            shutil.move(src, dst)

        for name in names:
            if os.path.isfile(name):
                add_archive(name)
            else:
                add_manual(name)

    def remove(self, names: List[str]) -> None:
        self.repository.process_remove(names)
        self._finalize()

    def report(self, target: Optional[List[str]] = None) -> None:
        targets = target or None
        self.repository.process_report(targets)

    def sync(self, target: Optional[List[str]] = None) -> None:
        targets = target or None
        self.repository.process_sync(targets)

    def update(self, updates: List[Package]) -> None:
        packages = self.repository.process_build(updates)
        self.repository.process_update(packages)
        self._finalize()

