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
from dataclasses import asdict
from typing import Any, Dict

from aiohttp.web import View

from ahriman.core.watcher.watcher import Watcher
from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package


class BaseView(View):
    '''
    base web view to make things typed
    '''

    @property
    def service(self) -> Watcher:
        '''
        :return: build status watcher instance
        '''
        watcher: Watcher = self.request.app['watcher']
        return watcher

    @staticmethod
    def package_view(package: Package, status: BuildStatus) -> Dict[str, Any]:
        '''
        generate json package view
        :param package: package definitions
        :param status: package build status
        :return: json-friendly dictionary
        '''
        return {
            'status': BaseView.status_view(status),
            'package': asdict(package)
        }

    @staticmethod
    def status_view(status: BuildStatus) -> Dict[str, Any]:
        '''
        generate json status view
        :param status: build status
        :return: json-friendly dictionary
        '''
        return {
            'status': status.status.value,
            'timestamp': status.timestamp
        }
