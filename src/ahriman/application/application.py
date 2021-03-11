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
from __future__ import annotations

import argparse
import logging
import os
import shutil

from typing import Callable, Iterable, List, Optional, Set, Type

from ahriman.core.build_tools.task import Task
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.core.tree import Tree
from ahriman.models.package import Package


class Application:

    def __init__(self, architecture: str, config: Configuration) -> None:
        self.logger = logging.getLogger('root')
        self.config = config
        self.architecture = architecture
        self.repository = Repository(architecture, config)

    @classmethod
    def from_args(cls: Type[Application], args: argparse.Namespace) -> Application:
        config = Configuration.from_path(args.config)
        return cls(args.architecture, config)

    def _known_packages(self) -> Set[str]:
        known_packages = set()
        # local set
        for package in self.repository.packages():
            known_packages.update(package.packages)
        known_packages.update(self.repository.pacman.all_packages())
        return known_packages

    def _finalize(self) -> None:
        self.report()
        self.sync()

    def get_updates(self, no_aur: bool, no_manual: bool, no_vcs: bool,
                    log_fn: Callable[[str], None]) -> List[Package]:
        updates = []

        if not no_aur:
            updates.extend(self.repository.updates_aur(no_vcs))
        if not no_manual:
            updates.extend(self.repository.updates_manual())

        for package in updates:
            log_fn(f'{package.base} = {package.version}')

        return updates

    def add(self, names: Iterable[str], without_dependencies: bool) -> None:
        known_packages = self._known_packages()

        def add_manual(name: str) -> str:
            package = Package.load(name, self.repository.pacman, self.config.get('alpm', 'aur_url'))
            path = os.path.join(self.repository.paths.manual, package.base)
            Task.fetch(path, package.git_url)
            return path

        def add_archive(src: str) -> None:
            dst = os.path.join(self.repository.paths.packages, os.path.basename(src))
            shutil.move(src, dst)

        def process_dependencies(path: str) -> None:
            if without_dependencies:
                return
            dependencies = Package.dependencies(path)
            self.add(dependencies.difference(known_packages), without_dependencies)

        def process_single(name: str) -> None:
            if not os.path.isfile(name):
                path = add_manual(name)
                process_dependencies(path)
            else:
                add_archive(name)

        for name in names:
            process_single(name)

    def remove(self, names: Iterable[str]) -> None:
        self.repository.process_remove(names)
        self._finalize()

    def report(self, target: Optional[Iterable[str]] = None) -> None:
        targets = target or None
        self.repository.process_report(targets)

    def sync(self, target: Optional[Iterable[str]] = None) -> None:
        targets = target or None
        self.repository.process_sync(targets)

    def update(self, updates: Iterable[Package]) -> None:
        def process_single(portion: Iterable[Package]):
            packages = self.repository.process_build(portion)
            self.repository.process_update(packages)
            self._finalize()

        tree = Tree()
        tree.load(updates)
        for num, level in enumerate(tree.levels()):
            self.logger.info(f'processing level #{num} {[package.base for package in level]}')
            process_single(level)