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

from ahriman.core.build_tools.sources import Sources
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import GitRemoteFailed
from ahriman.core.lazy_logging import LazyLogging
from ahriman.core.util import walk
from ahriman.models.package_source import PackageSource
from ahriman.models.remote_source import RemoteSource


class RemotePull(LazyLogging):
    """
    fetch PKGBUILDs from remote repository and use them for following actions

    Attributes:
        remote_source(RemoteSource): repository remote source (remote pull url and branch)
        repository_paths(RepositoryPaths): repository paths instance
    """

    def __init__(self, configuration: Configuration, section: str) -> None:
        """
        default constructor

        Args:
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
        self.repository_paths = configuration.repository_paths

    def repo_clone(self) -> None:
        """
        clone repository from remote source
        """
        with TemporaryDirectory(ignore_cleanup_errors=True) as dir_name, (clone_dir := Path(dir_name)):
            Sources.fetch(clone_dir, self.remote_source)
            self.repo_copy(clone_dir)

    def repo_copy(self, clone_dir: Path) -> None:
        """
        copy directories from cloned remote source to local cache

        Args:
            clone_dir(Path): path to temporary cloned directory
        """
        for pkgbuild_path in filter(lambda path: path.name == "PKGBUILD", walk(clone_dir)):
            cloned_pkgbuild_dir = pkgbuild_path.parent
            package_base = cloned_pkgbuild_dir.name
            local_pkgbuild_dir = self.repository_paths.cache_for(package_base)
            shutil.copytree(cloned_pkgbuild_dir, local_pkgbuild_dir, dirs_exist_ok=True)
            Sources.init(local_pkgbuild_dir)  # initialized git repository is required for local sources

    def run(self) -> None:
        """
        run git pull action
        """
        try:
            self.repo_clone()
        except Exception:
            self.logger.exception("git pull failed")
            raise GitRemoteFailed()
