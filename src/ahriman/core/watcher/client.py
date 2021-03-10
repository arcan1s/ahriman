#
# Copyright (c) 2021 Evgenii Alekseev.
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
from __future__ import annotations

import logging

from typing import Any, Dict, Set

from ahriman.core.configuration import Configuration
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package


class Client:

    def add(self, package: Package, status: BuildStatusEnum) -> None:
        pass

    def remove(self, base: str, packages: Set[str]) -> None:
        pass

    def update(self, base: str, status: BuildStatusEnum) -> None:
        pass

    @staticmethod
    def load(config: Configuration) -> Client:
        host = config.get('web', 'host', fallback=None)
        port = config.getint('web', 'port', fallback=None)
        if host is None or port is None:
            return Client()
        return WebClient(host, port)


class WebClient(Client):

    def __init__(self, host: str, port: int) -> None:
        self.logger = logging.getLogger('http')
        self.host = host
        self.port = port

    def _url(self, base: str) -> str:
        return f'http://{self.host}:{self.port}/api/v1/packages/{base}'

    def add(self, package: Package, status: BuildStatusEnum) -> None:
        import requests

        payload: Dict[str, Any] = {
            'status': status.value,
            'base': package.base,
            'packages': [p for p in package.packages],
            'version': package.version,
            'url': package.web_url
        }

        try:
            response = requests.post(self._url(package.base), json=payload)
            response.raise_for_status()
        except:
            self.logger.exception(f'could not add {package.base}', exc_info=True)

    def remove(self, base: str, packages: Set[str]) -> None:
        if not packages:
            return
        import requests

        try:
            response = requests.delete(self._url(base))
            response.raise_for_status()
        except:
            self.logger.exception(f'could not delete {base}', exc_info=True)

    def update(self, base: str, status: BuildStatusEnum) -> None:
        import requests

        payload: Dict[str, Any] = {'status': status.value}

        try:
            response = requests.post(self._url(base), json=payload)
            response.raise_for_status()
        except:
            self.logger.exception(f'could not update {base}', exc_info=True)