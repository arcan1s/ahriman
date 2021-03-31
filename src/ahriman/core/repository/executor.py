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
import shutil

from pathlib import Path
from typing import Dict, Iterable, List, Optional

from ahriman.core.build_tools.task import Task
from ahriman.core.report.report import Report
from ahriman.core.repository.cleaner import Cleaner
from ahriman.core.upload.upload import Upload
from ahriman.models.package import Package


class Executor(Cleaner):
    """
    trait for common repository update processes
    """

    def packages(self) -> List[Package]:
        """
        generate list of repository packages
        :return: list of packages properties
        """
        raise NotImplementedError

    def process_build(self, updates: Iterable[Package]) -> List[Path]:
        """
        build packages
        :param updates: list of packages properties to build
        :return: `packages_built`
        """
        def build_single(package: Package) -> None:
            self.reporter.set_building(package.base)
            task = Task(package, self.configuration, self.paths)
            task.init()
            built = task.build()
            for src in built:
                dst = self.paths.packages / src.name
                shutil.move(src, dst)

        for single in updates:
            try:
                build_single(single)
            except Exception:
                self.reporter.set_failed(single.base)
                self.logger.exception(f"{single.base} ({self.architecture}) build exception")
        self.clear_build()

        return self.packages_built()

    def process_remove(self, packages: Iterable[str]) -> Path:
        """
        remove packages from list
        :param packages: list of package names or bases to remove
        :return: path to repository database
        """
        def remove_single(package: str, fn: Path) -> None:
            try:
                self.repo.remove(package, fn)
            except Exception:
                self.logger.exception(f"could not remove {package}")

        requested = set(packages)
        for local in self.packages():
            if local.base in packages or all(package in requested for package in local.packages):
                to_remove = {
                    package: Path(properties.filename)
                    for package, properties in local.packages.items()
                    if properties.filename is not None
                }
                self.reporter.remove(local.base)  # we only update status page in case of base removal
            elif requested.intersection(local.packages.keys()):
                to_remove = {
                    package: Path(properties.filename)
                    for package, properties in local.packages.items()
                    if package in requested and properties.filename is not None
                }
            else:
                to_remove = dict()
            for package, filename in to_remove.items():
                remove_single(package, filename)

        return self.repo.repo_path

    def process_report(self, targets: Optional[Iterable[str]]) -> None:
        """
        generate reports
        :param targets: list of targets to generate reports. Configuration option will be used if it is not set
        """
        if targets is None:
            targets = self.configuration.getlist("report", "target")
        for target in targets:
            runner = Report.load(self.architecture, self.configuration, target)
            runner.run(self.packages())

    def process_sync(self, targets: Optional[Iterable[str]]) -> None:
        """
        process synchronization to remote servers
        :param targets: list of targets to sync. Configuration option will be used if it is not set
        """
        if targets is None:
            targets = self.configuration.getlist("upload", "target")
        for target in targets:
            runner = Upload.load(self.architecture, self.configuration, target)
            runner.run(self.paths.repository)

    def process_update(self, packages: Iterable[Path]) -> Path:
        """
        sign packages, add them to repository and update repository database
        :param packages: list of filenames to run
        :return: path to repository database
        """
        def update_single(fn: Optional[str], base: str) -> None:
            if fn is None:
                self.logger.warning(f"received empty package name for base {base}")
                return  # suppress type checking, it never can be none actually
            # in theory it might be NOT packages directory, but we suppose it is
            full_path = self.paths.packages / fn
            files = self.sign.sign_package(full_path, base)
            for src in files:
                dst = self.paths.repository / src.name
                shutil.move(src, dst)
            package_path = self.paths.repository / fn
            self.repo.add(package_path)

        # we are iterating over bases, not single packages
        updates: Dict[str, Package] = {}
        for filename in packages:
            try:
                local = Package.load(filename, self.pacman, self.aur_url)
                updates.setdefault(local.base, local).packages.update(local.packages)
            except Exception:
                self.logger.exception(f"could not load package from {filename}")

        for local in updates.values():
            try:
                for description in local.packages.values():
                    update_single(description.filename, local.base)
                self.reporter.set_success(local)
            except Exception:
                self.reporter.set_failed(local.base)
                self.logger.exception(f"could not process {local.base}")
        self.clear_packages()

        return self.repo.repo_path
