#
# Copyright (c) 2021-2023 ahriman team.
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

from collections.abc import Generator
from pathlib import Path
from tempfile import TemporaryDirectory

from ahriman.core.build_tools.sources import Sources
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import GitRemoteError
from ahriman.core.log import LazyLogging
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.remote_source import RemoteSource
from ahriman.models.result import Result


class RemotePush(LazyLogging):
    """
    sync PKGBUILDs to remote repository after actions

    Attributes:
        commit_author(str | None): optional commit author in form of git config (i.e. ``user <user@host>``)
        database(SQLite): database instance
        remote_source(RemoteSource): repository remote source (remote pull url and branch)
    """

    def __init__(self, database: SQLite, configuration: Configuration, section: str) -> None:
        """
        default constructor

        Args:
            database(SQLite): database instance
            configuration(Configuration): configuration instance
            section(str): settings section name
        """
        self.database = database
        self.commit_author = configuration.get(section, "commit_author", fallback=None)
        self.remote_source = RemoteSource(
            git_url=configuration.get(section, "push_url"),
            web_url="",
            path=".",
            branch=configuration.get(section, "push_branch", fallback="master"),
            source=PackageSource.Local,
        )

    def package_update(self, package: Package, target_dir: Path) -> str:
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
        # ...secondly, we clone whole tree...
        Sources.fetch(package_target_dir, package.remote)
        # ...and last, but not least, we remove the dot-git directory...
        for git_file in package_target_dir.glob(".git*"):
            if git_file.is_file():
                git_file.unlink()
            else:
                shutil.rmtree(git_file)
        # ...copy all patches...
        for patch in self.database.patches_get(package.base):
            filename = f"ahriman-{package.base}.patch" if patch.key is None else f"ahriman-{patch.key}.patch"
            patch.write(package_target_dir / filename)
        # ...and finally return path to the copied directory
        return package.base

    def packages_update(self, result: Result, target_dir: Path) -> Generator[str, None, None]:
        """
        update all packages from the build result

        Args:
            result(Result): build result
            target_dir(Path): path to the cloned PKGBUILD repository

        Yields:
            str: path to updated files
        """
        for package in result.success:
            yield self.package_update(package, target_dir)

    def run(self, result: Result) -> None:
        """
        run git pull action

        Args:
            result(Result): build result
        """
        try:
            with TemporaryDirectory(ignore_cleanup_errors=True) as dir_name:
                clone_dir = Path(dir_name)
                Sources.fetch(clone_dir, self.remote_source)
                Sources.push(clone_dir, self.remote_source, *self.packages_update(result, clone_dir),
                             commit_author=self.commit_author)
        except Exception:
            self.logger.exception("git push failed")
            raise GitRemoteError()
