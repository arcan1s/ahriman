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
from typing import Generator

from ahriman.core.build_tools.sources import Sources
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import GitRemoteFailed
from ahriman.core.lazy_logging import LazyLogging
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.remote_source import RemoteSource
from ahriman.models.result import Result


class RemotePush(LazyLogging):
    """
    sync PKGBUILDs to remote repository after actions

    Attributes:
        remote_source(RemoteSource): repository remote source (remote pull url and branch)
    """

    def __init__(self, configuration: Configuration, section: str) -> None:
        """
        default constructor

        Args:
            configuration(Configuration): configuration instance
            remote_push_trigger.py
        """
        self.remote_source = RemoteSource(
            git_url=configuration.get(section, "push_url"),
            web_url="",
            path=".",
            branch=configuration.get(section, "push_branch", fallback="master"),
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
            yield RemotePush.package_update(package, target_dir)

    def run(self, result: Result) -> None:
        """
        run git pull action

        Args:
            result(Result): build result
        """
        try:
            with TemporaryDirectory(ignore_cleanup_errors=True) as dir_name, (clone_dir := Path(dir_name)):
                Sources.fetch(clone_dir, self.remote_source)
                Sources.push(clone_dir, self.remote_source, *RemotePush.packages_update(result, clone_dir))
        except Exception:
            self.logger.exception("git push failed")
            raise GitRemoteFailed()
