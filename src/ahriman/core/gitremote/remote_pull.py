#
# Copyright (c) 2021-2026 ahriman team.
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
from tempfile import TemporaryDirectory

from ahriman.core.build_tools.sources import Sources
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import GitRemoteError
from ahriman.core.log import LazyLogging
from ahriman.core.utils import walk
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.remote_source import RemoteSource
from ahriman.models.repository_id import RepositoryId


class RemotePull(LazyLogging):
    """
    fetch PKGBUILDs from remote repository and use them for following actions

    Attributes:
        architecture(str): repository architecture
        remote_source(RemoteSource): repository remote source (remote pull url and branch)
        repository_paths(RepositoryPaths): repository paths instance
    """

    def __init__(self, repository_id: RepositoryId, configuration: Configuration, section: str) -> None:
        """
        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            section(str): settings section name
        """
        self.remote_source = RemoteSource(
            git_url=configuration.get(section, "pull_url"),
            web_url="",
            path=".",
            branch=configuration.get(section, "pull_branch", fallback="master"),
            source=PackageSource.Local,
        )
        self.architecture = repository_id.architecture
        self.repository_paths = configuration.repository_paths

    def package_copy(self, pkgbuild_path: Path) -> None:
        """
        copy single PKGBUILD content to the repository tree

        Args:
            pkgbuild_path(Path): path to PKGBUILD to copy
        """
        cloned_pkgbuild_dir = pkgbuild_path.parent

        # load package from the PKGBUILD, because it might be possible that name doesn't match
        # e.g. if we have just cloned repo with just one PKGBUILD
        package = Package.from_build(cloned_pkgbuild_dir, self.architecture, None)
        package_base = package.base
        local_pkgbuild_dir = self.repository_paths.cache_for(package_base)

        # copy source ignoring the git files
        shutil.copytree(cloned_pkgbuild_dir, local_pkgbuild_dir,
                        ignore=shutil.ignore_patterns(".git*"), dirs_exist_ok=True)
        # initialized git repository is required for local sources
        Sources.init(local_pkgbuild_dir)

    def repo_clone(self) -> None:
        """
        clone repository from remote source
        """
        with TemporaryDirectory(ignore_cleanup_errors=True) as dir_name:
            clone_dir = Path(dir_name)
            Sources.fetch(clone_dir, self.remote_source)
            self.repo_copy(clone_dir)

    def repo_copy(self, clone_dir: Path) -> None:
        """
        copy directories from cloned remote source to local cache

        Args:
            clone_dir(Path): path to temporary cloned directory
        """
        for pkgbuild_path in filter(lambda path: path.name == "PKGBUILD", walk(clone_dir)):
            self.package_copy(pkgbuild_path)

    def run(self) -> None:
        """
        run git pull action

        Raises:
            GitRemoteError: pull processing error
        """
        try:
            self.repo_clone()
        except Exception:
            self.logger.exception("git pull failed")
            raise GitRemoteError
