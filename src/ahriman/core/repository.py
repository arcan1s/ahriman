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

from typing import Dict, List, Optional

from ahriman.core.build_tools.task import Task
from ahriman.core.configuration import Configuration
from ahriman.core.repo.repo_wrapper import RepoWrapper
from ahriman.core.report.report import Report
from ahriman.core.sign.gpg_wrapper import GPGWrapper
from ahriman.core.upload.uploader import Uploader
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


class Repository:

    def __init__(self, architecture: str, config: Configuration) -> None:
        self.logger = logging.getLogger('builder')
        self.architecture = architecture
        self.config = config

        self.aur_url = config.get('aur', 'url')
        self.name = config.get('repository', 'name')

        self.paths = RepositoryPaths(config.get('repository', 'root'), self.architecture)
        self.paths.create_tree()

        self.sign = GPGWrapper(config)
        self.wrapper = RepoWrapper(self.name, self.paths)

    def _clear_build(self) -> None:
        for package in os.listdir(self.paths.sources):
            shutil.rmtree(os.path.join(self.paths.sources, package))

    def _clear_manual(self) -> None:
        for package in os.listdir(self.paths.manual):
            shutil.rmtree(os.path.join(self.paths.manual, package))

    def _clear_packages(self) -> None:
        for package in os.listdir(self.paths.packages):
            os.remove(os.path.join(self.paths.packages, package))

    def packages(self) -> List[Package]:
        result: Dict[str, Package] = {}
        for fn in os.listdir(self.paths.repository):
            if '.pkg.' not in fn:
                continue
            full_path = os.path.join(self.paths.repository, fn)
            try:
                local = Package.load(full_path, self.aur_url)
                if local.name in result:
                    continue
                result[local.name] = local
            except Exception:
                self.logger.exception(f'could not load package from {fn}', exc_info=True)
                continue
        return list(result.values())

    def process_build(self, updates: List[Package]) -> List[str]:
        def build_single(package: Package) -> None:
            task = Task(package, self.architecture, self.config, self.paths)
            task.fetch()
            built = task.build()
            for src in built:
                dst = os.path.join(self.paths.packages, os.path.basename(src))
                shutil.move(src, dst)

        for package in updates:
            try:
                build_single(package)
            except Exception:
                self.logger.exception(f'{package.name} ({self.architecture}) build exception', exc_info=True)
                continue
        self._clear_build()

        return [
            os.path.join(self.paths.packages, fn)
            for fn in os.listdir(self.paths.packages)
        ]

    def process_remove(self, packages: List[str]) -> str:
        for fn in os.listdir(self.paths.repository):
            if '.pkg.' not in fn:
                continue

            full_path = os.path.join(self.paths.repository, fn)
            try:
                local = Package.load(full_path, self.aur_url)
                if local.name not in packages:
                    continue
                self.wrapper.remove(full_path, local.name)
            except Exception:
                self.logger.exception(f'could not load package from {fn}', exc_info=True)
                continue

        self.sign.sign_repository(self.wrapper.repo_path)
        return self.wrapper.repo_path

    def process_report(self, targets: Optional[List[str]]) -> None:
        if targets is None:
            targets = self.config.get_list('report', 'target')
        for target in targets:
            Report.run(self.architecture, self.config, target, self.paths.repository)

    def process_sync(self, targets: Optional[List[str]]) -> None:
        if targets is None:
            targets = self.config.get_list('upload', 'target')
        for target in targets:
            Uploader.run(self.architecture, self.config, target, self.paths.repository)

    def process_update(self, packages: List[str]) -> str:
        for package in packages:
            files = self.sign.sign_package(package)
            for src in files:
                dst = os.path.join(self.paths.repository, os.path.basename(src))
                shutil.move(src, dst)
            package_fn = os.path.join(self.paths.repository, os.path.basename(package))
            self.wrapper.add(package_fn)
        self._clear_packages()

        self.sign.sign_repository(self.wrapper.repo_path)
        return self.wrapper.repo_path

    def updates_aur(self, checked: List[str]) -> List[Package]:
        result: List[Package] = []
        ignore_list = self.config.get_list(
            self.config.get_section_name('build', self.architecture), 'ignore_packages')

        for fn in os.listdir(self.paths.repository):
            if '.pkg.' not in fn:
                continue

            try:
                local = Package.load(os.path.join(self.paths.repository, fn), self.aur_url)
                remote = Package.load(local.name, self.aur_url)
            except Exception:
                self.logger.exception(f'could not load package from {fn}', exc_info=True)
                continue
            if local.name in checked:
                continue
            if local.name in ignore_list:
                continue

            if local.is_outdated(remote):
                result.append(remote)
            checked.append(local.name)

        return result

    def updates_manual(self, checked: List[str]) -> List[Package]:
        result: List[Package] = []

        for fn in os.listdir(self.paths.manual):
            local = Package.load(os.path.join(self.paths.manual, fn), self.aur_url)
            if local.name in checked:
                continue
            result.append(local)
            checked.append(local.name)
        self._clear_manual()

        return result