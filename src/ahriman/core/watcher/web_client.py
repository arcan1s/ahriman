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
import logging
import requests

from dataclasses import asdict
from typing import Any, Dict

from ahriman.core.watcher.client import Client
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package


class WebClient(Client):
    '''
    build status reporter web client
    :ivar host: host of web service
    :ivar logger: class logger
    :ivar port: port of web service
    '''

    def __init__(self, host: str, port: int) -> None:
        '''
        default constructor
        :param host: host of web service
        :param port: port of web service
        '''
        self.logger = logging.getLogger('http')
        self.host = host
        self.port = port

    def _url(self, base: str) -> str:
        '''
        url generator
        :param base: package base to generate url
        :return: full url of web service for specific package base
        '''
        return f'http://{self.host}:{self.port}/api/v1/packages/{base}'

    def add(self, package: Package, status: BuildStatusEnum) -> None:
        '''
        add new package with status
        :param package: package properties
        :param status: current package build status
        '''
        payload: Dict[str, Any] = {
            'status': status.value,
            'package': asdict(package)
        }

        try:
            response = requests.post(self._url(package.base), json=payload)
            response.raise_for_status()
        except Exception:
            self.logger.exception(f'could not add {package.base}', exc_info=True)

    def remove(self, base: str) -> None:
        '''
        remove packages from watcher
        :param base: basename to remove
        '''
        try:
            response = requests.delete(self._url(base))
            response.raise_for_status()
        except Exception:
            self.logger.exception(f'could not delete {base}', exc_info=True)

    def update(self, base: str, status: BuildStatusEnum) -> None:
        '''
        update package build status. Unlike `add` it does not update package properties
        :param base: package base to update
        :param status: current package build status
        '''
        payload: Dict[str, Any] = {'status': status.value}

        try:
            response = requests.post(self._url(base), json=payload)
            response.raise_for_status()
        except Exception:
            self.logger.exception(f'could not update {base}', exc_info=True)
