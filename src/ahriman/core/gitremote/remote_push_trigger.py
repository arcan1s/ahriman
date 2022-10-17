#
# copyright (c) 2021-2022 ahriman team.
#
# this file is part of ahriman
# (see https://github.com/arcan1s/ahriman).
#
# this program is free software: you can redistribute it and/or modify
# it under the terms of the gnu general public license as published by
# the free software foundation, either version 3 of the license, or
# (at your option) any later version.
#
# this program is distributed in the hope that it will be useful,
# but without any warranty; without even the implied warranty of
# merchantability or fitness for a particular purpose.  see the
# gnu general public license for more details.
#
# you should have received a copy of the gnu general public license
# along with this program. if not, see <http://www.gnu.org/licenses/>.
#
import shutil

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator, Iterable

from ahriman.core.build_tools.sources import Sources
from ahriman.core.configuration import Configuration
from ahriman.core.triggers import Trigger
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.remote_source import RemoteSource
from ahriman.models.result import Result


class RemotePushTrigger(Trigger):
    """
    trigger for syncing PKGBUILDs to remote repository

    Attributes:
        remote_source(RemoteSource): repository remote source (remote pull url and branch)
    """

    def __init__(self, architecture: str, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
        """
        Trigger.__init__(self, architecture, configuration)
        self.remote_source = RemoteSource(
            git_url=configuration.get("gitremote", "push_url"),
            web_url="",
            path=".",
            branch=configuration.get("gitremote", "push_branch", fallback="master"),
            source=PackageSource.Local,
        )

    @staticmethod
    def package_update(package: Package, target_dir: Path) -> str:
        """
        clone specified package and update its content in cloned PKGBUILD repository

        Args:
            package(Package): built package to update pkgbuild repository
            target_dir(Path): path to the cloned PKGBUILD repository

        Returns:
            str: relative path to be added as new file
        """
        # instead of iterating by directory we can simplify the process
        # firstly, we need to remove old data to make sure that removed files are not tracked anymore...
        package_target_dir = target_dir / package.base
        shutil.rmtree(package_target_dir, ignore_errors=True)
        # ...secondly, we copy whole tree...
        with TemporaryDirectory(ignore_cleanup_errors=True) as dir_name, (clone_dir := Path(dir_name)):
            Sources.fetch(clone_dir, package.remote)
            shutil.copytree(clone_dir, package_target_dir)
        # ...and last, but not least, we remove the dot-git directory...
        shutil.rmtree(package_target_dir / ".git", ignore_errors=True)
        # ...and finally return path to the copied directory
        return package.base

    @staticmethod
    def packages_update(result: Result, target_dir: Path) -> Generator[str, None, None]:
        """
        update all packages from the build result

        Args:
            result(Result): build result
            target_dir(Path): path to the cloned PKGBUILD repository

        Yields:
            str: path to updated files
        """
        for package in result.success:
            yield RemotePushTrigger.package_update(package, target_dir)

    def on_result(self, result: Result, packages: Iterable[Package]) -> None:
        """
        trigger action which will be called after build process with process result

        Args:
            result(Result): build result
            packages(Iterable[Package]): list of all available packages
        """
        with TemporaryDirectory(ignore_cleanup_errors=True) as dir_name, (clone_dir := Path(dir_name)):
            Sources.fetch(clone_dir, self.remote_source)
            Sources.push(clone_dir, self.remote_source, *RemotePushTrigger.packages_update(result, clone_dir))
