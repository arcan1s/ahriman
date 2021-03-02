import logging
import os

from ahriman.core.exceptions import BuildFailed
from ahriman.core.util import check_output
from ahriman.models.repository_paths import RepositoryPaths


class RepoWrapper:

    def __init__(self, name: str, paths: RepositoryPaths) -> None:
        self.logger = logging.getLogger('build_details')
        self.name = name
        self.paths = paths

    @property
    def repo_path(self) -> str:
        return os.path.join(self.paths.repository, f'{self.name}.db.tar.gz')

    def add(self, path: str) -> None:
        check_output(
            'repo-add', '-R', self.repo_path, path,
            exception=BuildFailed(path),
            cwd=self.paths.repository,
            logger=self.logger)

    def remove(self, path: str, package: str) -> None:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        try:
            os.remove(f'{path}.sig')  # sign if any
        except FileNotFoundError:
            pass
        check_output(
            'repo-remove', self.repo_path, package,
            exception=BuildFailed(path),
            cwd=self.paths.repository,
            logger=self.logger)
