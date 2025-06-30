#
# Copyright (c) 2021-2025 ahriman team.
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

from typing import Any, ClassVar

from ahriman.core.auth.helpers import authorized_userid
from ahriman.core.utils import pretty_interval
from ahriman.models.user_access import UserAccess
from ahriman.web.apispec import aiohttp_apispec
from ahriman.web.views.base import BaseView


class IndexView(BaseView):
    """
    root view

    It uses jinja2 templates for report generation, the following variables are allowed:

        * auth - authorization descriptor, required
            * control - HTML to insert for login control, HTML string, required
            * enabled - whether authorization is enabled by configuration or not, boolean, required
            * username - authenticated username if any, string, null means not authenticated
        * autorefresh_intervals - auto refresh intervals, optional
            * interval - auto refresh interval in milliseconds, integer, required
            * is_active - is current interval active or not, boolean, required
            * text - text representation of the interval (e.g. "30 seconds"), string, required
        * docs_enabled - indicates if api docs is enabled, boolean, required
        * index_url - url to the repository index, string, optional
        * repositories - list of repositories unique identifiers, required
            * id - unique repository identifier, string, required
            * repository - repository name, string, required
            * architecture - repository architecture, string, required

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
    """

    GET_PERMISSION: ClassVar[UserAccess] = UserAccess.Unauthorized
    ROUTES = ["/", "/index.html"]

    @aiohttp_jinja2.template("build-status.jinja2")
    async def get(self) -> dict[str, Any]:
        """
        process get request. No parameters supported here

        Returns:
            dict[str, Any]: parameters for jinja template
        """
        auth_username = await authorized_userid(self.request)
        auth = {
            "control": self.validator.auth_control,
            "enabled": self.validator.enabled,
            "username": auth_username,
        }

        autorefresh_intervals = [
            {
                "interval": interval * 1000,  # milliseconds
                "is_active": index == 0,
                "text": pretty_interval(interval),
            }
            for index, interval in enumerate(self.configuration.getintlist("web", "autorefresh_intervals", fallback=[]))
        ]

        return {
            "auth": auth,
            "autorefresh_intervals": sorted(autorefresh_intervals, key=lambda interval: interval["interval"]),
            "docs_enabled": aiohttp_apispec is not None,
            "index_url": self.configuration.get("web", "index_url", fallback=None),
            "repositories": [
                {
                    "id": repository.id,
                    **repository.view(),
                }
                for repository in sorted(self.services)
            ]
        }
