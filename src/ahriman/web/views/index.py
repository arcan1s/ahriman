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
import aiohttp_jinja2  # type: ignore

from typing import Any, Dict

import ahriman.version as version

from ahriman.web.views.base import BaseView


class IndexView(BaseView):
    '''
    root view

    It uses jinja2 templates for report generation, the following variables are allowed:

        architecture - repository architecture, string, required
        packages - sorted list of packages properties: base, packages (sorted list), status,
                   timestamp, version, web_url. Required
        repository - repository name, string, required
        service - service status properties: status, status_color, timestamp. Required
        version - ahriman version, string, required
    '''

    @aiohttp_jinja2.template("build-status.jinja2")  # type: ignore
    async def get(self) -> Dict[str, Any]:
        '''
        process get request. No parameters supported here
        :return: parameters for jinja template
        '''
        # some magic to make it jinja-friendly
        packages = [
            {
                'base': package.base,
                'packages': [p for p in sorted(package.packages)],
                'status': status.status.value,
                'timestamp': status.timestamp,
                'version': package.version,
                'web_url': package.web_url
            } for package, status in sorted(self.service.packages, key=lambda item: item[0].base)
        ]
        service = {
            'status': self.service.status.status.value,
            'status_color': self.service.status.status.badges_color(),
            'timestamp': self.service.status.timestamp
        }

        return {
            'architecture': self.service.architecture,
            'packages': packages,
            'repository': self.service.repository.name,
            'service': service,
            'version': version.__version__,
        }
