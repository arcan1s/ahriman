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
    '''
    base repository control class
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
    '''

    def __init__(self, architecture: str, config: Configuration) -> None:
        '''
        default constructor
        :param architecture: repository architecture
        :param config: configuration instance
        '''
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
        self.reporter = Client.load(architecture, config)

    def _clear_build(self) -> None:
        '''
        clear sources directory
        '''
        for package in os.listdir(self.paths.sources):
            shutil.rmtree(os.path.join(self.paths.sources, package))

    def _clear_manual(self) -> None:
        '''
        clear directory with manual package updates
        '''
        for package in os.listdir(self.paths.manual):
            shutil.rmtree(os.path.join(self.paths.manual, package))

    def _clear_packages(self) -> None:
        '''
        clear directory with built packages (NOT repository itself)
        '''
        for package in self.packages_built():
            os.remove(package)

    def packages(self) -> List[Package]:
        '''
        generate list of repository packages
        :return: list of packages properties
        '''
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
        '''
        get list of files in built packages directory
        :return: list of filenames from the directory
        '''
        return [
            os.path.join(self.paths.packages, fn)
            for fn in os.listdir(self.paths.packages)
        ]

    def process_build(self, updates: Iterable[Package]) -> List[str]:
        '''
        build packages
        :param updates: list of packages properties to build
        :return: `packages_built`
        '''
        def build_single(package: Package) -> None:
            self.reporter.set_building(package.base)
            task = Task(package, self.architecture, self.config, self.paths)
            task.init()
            built = task.build()
            for src in built:
                dst = os.path.join(self.paths.packages, os.path.basename(src))
                shutil.move(src, dst)

        for package in updates:
            try:
                build_single(package)
            except Exception:
                self.reporter.set_failed(package.base)
                self.logger.exception(f'{package.base} ({self.architecture}) build exception', exc_info=True)
                continue
        self._clear_build()

        return self.packages_built()

    def process_remove(self, packages: Iterable[str]) -> str:
        '''
        remove packages from list
        :param packages: list of package names or bases to rmeove
        :return: path to repository database
        '''
        def remove_single(package: str) -> None:
            try:
                self.repo.remove(package)
            except Exception:
                self.logger.exception(f'could not remove {package}', exc_info=True)

        requested = set(packages)
        for local in self.packages():
            if local.base in packages:
                to_remove = set(local.packages.keys())
                self.reporter.remove(local.base)  # we only update status page in case of base removal
            elif requested.intersection(local.packages.keys()):
                to_remove = requested.intersection(local.packages.keys())
            else:
                to_remove = set()
            for package in to_remove:
                remove_single(package)

        return self.repo.repo_path

    def process_report(self, targets: Optional[Iterable[str]]) -> None:
        '''
        generate reports
        :param targets: list of targets to generate reports. Configuration option will be used if it is not set
        '''
        if targets is None:
            targets = self.config.getlist('report', 'target')
        for target in targets:
            Report.run(self.architecture, self.config, target, self.packages())

    def process_sync(self, targets: Optional[Iterable[str]]) -> None:
        '''
        process synchronization to remote servers
        :param targets: list of targets to sync. Configuration option will be used if it is not set
        '''
        if targets is None:
            targets = self.config.getlist('upload', 'target')
        for target in targets:
            Uploader.run(self.architecture, self.config, target, self.paths.repository)

    def process_update(self, packages: Iterable[str]) -> str:
        '''
        sign packages, add them to repository and update repository database
        :param packages: list of filenames to run
        :return: path to repository database
        '''
        for package in packages:
            local = Package.load(package, self.pacman, self.aur_url)  # we will use it for status reports
            try:
                files = self.sign.sign_package(package, local.base)
                for src in files:
                    dst = os.path.join(self.paths.repository, os.path.basename(src))
                    shutil.move(src, dst)
                package_fn = os.path.join(self.paths.repository, os.path.basename(package))
                self.repo.add(package_fn)
                self.reporter.set_success(local)
            except Exception:
                self.logger.exception(f'could not process {package}', exc_info=True)
                self.reporter.set_failed(local.base)
        self._clear_packages()

        return self.repo.repo_path

    def updates_aur(self, filter_packages: Iterable[str], no_vcs: bool) -> List[Package]:
        '''
        check AUR for updates
        :param filter_packages: do not check every package just specified in the list
        :param no_vcs: do not check VCS packages
        :return: list of packages which are out-of-dated
        '''
        result: List[Package] = []

        build_section = self.config.get_section_name('build', self.architecture)
        ignore_list = self.config.getlist(build_section, 'ignore_packages')

        for local in self.packages():
            if local.base in ignore_list:
                continue
            if local.is_vcs and no_vcs:
                continue
            if filter_packages and local.base not in filter_packages:
                continue

            try:
                remote = Package.load(local.base, self.pacman, self.aur_url)
                if local.is_outdated(remote, self.paths):
                    result.append(remote)
                    self.reporter.set_pending(local.base)
            except Exception:
                self.reporter.set_failed(local.base)
                self.logger.exception(f'could not load remote package {local.base}', exc_info=True)
                continue

        return result

    def updates_manual(self) -> List[Package]:
        '''
        check for packages for which manual update has been requested
        :return: list of packages which are out-of-dated
        '''
        result: List[Package] = []

        for fn in os.listdir(self.paths.manual):
            try:
                local = Package.load(os.path.join(self.paths.manual, fn), self.pacman, self.aur_url)
                result.append(local)
                self.reporter.set_unknown(local)
            except Exception:
                self.logger.exception(f'could not add package from {fn}', exc_info=True)
        self._clear_manual()

        return result
