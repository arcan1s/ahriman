import logging
import os

from typing import List

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import BuildFailed
from ahriman.core.util import check_output
from ahriman.models.sign_settings import SignSettings


class Sign:

    def __init__(self, config: Configuration) -> None:
        self.logger = logging.getLogger('build_details')

        self.key = config.get('sign', 'key', fallback=None)
        self.sign = SignSettings.from_option(config.get('sign', 'enabled'))

    def process(self, path: str) -> List[str]:
        cwd = os.path.dirname(path)
        check_output(
            *self.sign_cmd(path),
            exception=BuildFailed(path),
            cwd=os.path.dirname(path),
            logger=self.logger)
        return [path, f'{path}.sig']

    def sign_cmd(self, path: str) -> List[str]:
        cmd = ['gpg']
        if self.key is not None:
            cmd.extend(['-u', self.key])
        cmd.extend(['-b', path])
        return cmd

    def sign_package(self, path: str) -> List[str]:
        if self.sign != SignSettings.SignPackages:
            return [path]
        return self.process(path)

    def sign_repository(self, path: str) -> List[str]:
        if self.sign != SignSettings.SignRepository:
            return [path]
        return self.process(path)