import logging
import os
import shutil

from typing import List

from ahriman.core.configuration import Configuration
from ahriman.core.repo_wrapper import RepoWrapper
from ahriman.core.sign import Sign
from ahriman.core.task import Task
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


class Repository:

    def __init__(self, config: Configuration) -> None:
        self.logger = logging.getLogger('builder')
        self.config = config

        self.aur_url = config.get('aur', 'url')
        self.name = config.get('repository', 'name')

        self.paths = RepositoryPaths(config.get('repository', 'root'))
        self.paths.create_tree()

        self.sign = Sign(config)
        self.wrapper = RepoWrapper(self.name, self.paths)

    def _clear_build(self) -> None:
        for package in os.listdir(self.paths.sources):
            shutil.rmtree(os.path.join(self.paths.sources, package), ignore_errors=True)

    def _clear_manual(self) -> None:
        for package in os.listdir(self.paths.manual):
            shutil.rmtree(os.path.join(self.paths.manual, package), ignore_errors=True)

    def _clear_packages(self) -> None:
        for package in os.listdir(self.paths.packages):
            shutil.rmtree(os.path.join(self.paths.packages, package), ignore_errors=True)

    def process_build(self, updates: List[Package]) -> List[str]:
        for package in updates:
            try:
                task = Task(package, self.config, self.paths)
                task.fetch()
                built = task.build()
                for src in built:
                    dst = os.path.join(self.paths.packages, os.path.basename(src))
                    shutil.move(src, dst)
            except Exception:
                self.logger.exception(f'{package.name} build exception', exc_info=True)
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

    def updates(self) -> List[Package]:
        result: List[Package] = []
        checked_base: List[str] = []

        # repository updates
        for fn in os.listdir(self.paths.repository):
            if '.pkg.' not in fn:
                continue

            try:
                local = Package.load(os.path.join(self.paths.repository, fn), self.aur_url)
                remote = Package.load(local.name, self.aur_url)
            except Exception:
                self.logger.exception(f'could not load package from {fn}', exc_info=True)
                continue
            if local.name in checked_base:
                continue

            if local.is_outdated(remote):
                result.append(remote)
            checked_base.append(local.name)

        # manual updates
        for fn in os.listdir(self.paths.manual):
            local = Package.load(os.path.join(self.paths.manual, fn), self.aur_url)
            if local.name in checked_base:
                continue
            result.append(local)
            checked_base.append(local.name)
        self._clear_manual()

        return result