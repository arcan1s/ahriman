#
# Copyright (c) 2021 ahriman team.
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
import aiohttp_jinja2

from typing import Any, Dict

from ahriman import version
from ahriman.core.util import pretty_datetime
from ahriman.web.views.base import BaseView


class IndexView(BaseView):
    """
    root view

    It uses jinja2 templates for report generation, the following variables are allowed:

        architecture - repository architecture, string, required
        packages - sorted list of packages properties, required
                   * base, string
                   * depends, sorted list of strings
                   * groups, sorted list of strings
                   * licenses, sorted list of strings
                   * packages, sorted list of strings
                   * status, string based on enum value
                   * timestamp, pretty printed datetime, string
                   * version, string
                   * web_url, string
        repository - repository name, string, required
        service - service status properties, required
                   * status, string based on enum value
                   * status_color, string based on enum value
                   * timestamp, pretty printed datetime, string
        version - ahriman version, string, required
    """

    @aiohttp_jinja2.template("build-status.jinja2")
    async def get(self) -> Dict[str, Any]:
        """
        process get request. No parameters supported here
        :return: parameters for jinja template
        """
        # some magic to make it jinja-friendly
        packages = [
            {
                "base": package.base,
                "depends": package.depends,
                "groups": package.groups,
                "licenses": package.licenses,
                "packages": list(sorted(package.packages)),
                "status": status.status.value,
                "timestamp": pretty_datetime(status.timestamp),
                "version": package.version,
                "web_url": package.web_url
            } for package, status in sorted(self.service.packages, key=lambda item: item[0].base)
        ]
        service = {
            "status": self.service.status.status.value,
            "status_color": self.service.status.status.badges_color(),
            "timestamp": pretty_datetime(self.service.status.timestamp)
        }

        return {
            "architecture": self.service.architecture,
            "packages": packages,
            "repository": self.service.repository.name,
            "service": service,
            "version": version.__version__,
        }
