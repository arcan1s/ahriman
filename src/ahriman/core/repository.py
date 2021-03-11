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

from typing import Dict, Iterable, List, Optional

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.repo import Repo
from ahriman.core.build_tools.task import Task
from ahriman.core.configuration import Configuration
from ahriman.core.report.report import Report
from ahriman.core.sign.gpg import GPG
from ahriman.core.upload.uploader import Uploader
from ahriman.core.util import package_like
from ahriman.core.watcher.client import Client
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


class Repository:

    def __init__(self, architecture: str, config: Configuration) -> None:
        self.logger = logging.getLogger('builder')
        self.architecture = architecture
        self.config = config

        self.aur_url = config.get('alpm', 'aur_url')
        self.name = config.get('repository', 'name')

        self.paths = RepositoryPaths(config.get('repository', 'root'), architecture)
        self.paths.create_tree()

        self.pacman = Pacman(config)
        self.sign = GPG(architecture, config)
        self.repo = Repo(self.name, self.paths, self.sign.repository_sign_args)
        self.web = Client.load(architecture, config)

    def _clear_build(self) -> None:
        for package in os.listdir(self.paths.sources):
            shutil.rmtree(os.path.join(self.paths.sources, package))

    def _clear_manual(self) -> None:
        for package in os.listdir(self.paths.manual):
            shutil.rmtree(os.path.join(self.paths.manual, package))

    def _clear_packages(self) -> None:
        for package in self.packages_built():
            os.remove(package)

    def packages(self) -> List[Package]:
        result: Dict[str, Package] = {}
        for fn in os.listdir(self.paths.repository):
            if not package_like(fn):
                continue
            full_path = os.path.join(self.paths.repository, fn)
            try:
                local = Package.load(full_path, self.pacman, self.aur_url)
                result.setdefault(local.base, local).packages.update(local.packages)
            except Exception:
                self.logger.exception(f'could not load package from {fn}', exc_info=True)
                continue
        return list(result.values())

    def packages_built(self) -> List[str]:
        return [
            os.path.join(self.paths.packages, fn)
            for fn in os.listdir(self.paths.packages)
        ]

    def process_build(self, updates: Iterable[Package]) -> List[str]:
        def build_single(package: Package) -> None:
            self.web.set_building(package.base)
            task = Task(package, self.architecture, self.config, self.paths)
            task.clone()
            built = task.build()
            for src in built:
                dst = os.path.join(self.paths.packages, os.path.basename(src))
                shutil.move(src, dst)

        for package in updates:
            try:
                build_single(package)
            except Exception:
                self.web.set_failed(package.base)
                self.logger.exception(f'{package.base} ({self.architecture}) build exception', exc_info=True)
                continue
        self._clear_build()

        return self.packages_built()

    def process_remove(self, packages: Iterable[str]) -> str:
        def remove_single(package: str) -> None:
            try:
                self.repo.remove(package, package)
            except Exception:
                self.logger.exception(f'could not remove {package}', exc_info=True)

        for local in self.packages():
            if local.base in packages:
                to_remove = local.packages
            elif local.packages.intersection(packages):
                to_remove = local.packages.intersection(packages)
            else:
                to_remove = set()
            self.web.remove(local.base, to_remove)
            for package in to_remove:
                remove_single(package)

        return self.repo.repo_path

    def process_report(self, targets: Optional[Iterable[str]]) -> None:
        if targets is None:
            targets = self.config.getlist('report', 'target')
        for target in targets:
            Report.run(self.architecture, self.config, target, self.paths.repository)

    def process_sync(self, targets: Optional[Iterable[str]]) -> None:
        if targets is None:
            targets = self.config.getlist('upload', 'target')
        for target in targets:
            Uploader.run(self.architecture, self.config, target, self.paths.repository)

    def process_update(self, packages: Iterable[str]) -> str:
        for package in packages:
            local = Package.load(package, self.pacman, self.aur_url)  # we will use it for status reports
            try:
                files = self.sign.sign_package(package, local.base)
                for src in files:
                    dst = os.path.join(self.paths.repository, os.path.basename(src))
                    shutil.move(src, dst)
                package_fn = os.path.join(self.paths.repository, os.path.basename(package))
                self.repo.add(package_fn)
                self.web.set_success(local)
            except Exception:
                self.logger.exception(f'could not process {package}', exc_info=True)
                self.web.set_failed(local.base)
        self._clear_packages()

        return self.repo.repo_path

    def updates_aur(self, no_vcs: bool) -> List[Package]:
        result: List[Package] = []

        build_section = self.config.get_section_name('build', self.architecture)
        ignore_list = self.config.getlist(build_section, 'ignore_packages')

        for local in self.packages():
            if local.base in ignore_list:
                continue
            if local.is_vcs and no_vcs:
                continue

            try:
                remote = Package.load(local.base, self.pacman, self.aur_url)
                if local.is_outdated(remote):
                    result.append(remote)
                    self.web.set_pending(local.base)
            except Exception:
                self.web.set_failed(local.base)
                self.logger.exception(f'could not load remote package {local.base}', exc_info=True)
                continue

        return result

    def updates_manual(self) -> List[Package]:
        result: List[Package] = []

        for fn in os.listdir(self.paths.manual):
            try:
                local = Package.load(os.path.join(self.paths.manual, fn), self.pacman, self.aur_url)
                result.append(local)
                self.web.set_unknown(local)
            except Exception:
                self.logger.exception(f'could not add package from {fn}', exc_info=True)
        self._clear_manual()

        return result