import os
import logging
import shutil

from typing import List, Optional

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import BuildFailed
from ahriman.core.util import check_output
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


class Task:

    def __init__(self, package: Package, config: Configuration, paths: RepositoryPaths) -> None:
        self.logger = logging.getLogger('builder')
        self.build_logger = logging.getLogger('build_details')
        self.package = package
        self.paths = paths

        self.archbuild_flags = config.get('build', 'archbuild_flags').split()
        self.extra_build = config.get('build', 'extra_build')
        self.makepkg_flags = config.get('build', 'makepkg_flags').split()
        self.multilib_build = config.get('build', 'multilib_build')

    @property
    def git_path(self) -> str:
        return os.path.join(self.paths.sources, self.package.name)

    def build(self) -> List[str]:
        build_tool = self.multilib_build if self.package.is_multilib else self.extra_build

        cmd = [build_tool, '-r', self.paths.chroot]
        cmd.extend(self.archbuild_flags)
        if self.makepkg_flags:
            cmd.extend(['--', '--'] + self.makepkg_flags)
        self.logger.info(f'using {cmd} for {self.package.name}')

        check_output(
            *cmd,
            exception=BuildFailed(self.package.name),
            cwd=self.git_path,
            logger=self.build_logger)

        # well it is not actually correct, but we can deal with it
        return check_output('makepkg', '--packagelist',
                            exception=BuildFailed(self.package.name),
                            cwd=self.git_path).splitlines()

    def fetch(self, path: Optional[str] = None) -> None:
        git_path = path or self.git_path
        shutil.rmtree(git_path, ignore_errors=True)
        check_output('git', 'clone', self.package.url, git_path, exception=None)
