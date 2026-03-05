#
# Copyright (c) 2021-2026 ahriman team.
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

from aiohttp.web import Response
from typing import ClassVar

from ahriman.models.user_access import UserAccess
from ahriman.web.server_info import server_info
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
        * version - service version, string, required

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
    """

    GET_PERMISSION: ClassVar[UserAccess] = UserAccess.Unauthorized
    ROUTES = ["/", "/index.html"]

    async def get(self) -> Response:
        """
        process get request. No parameters supported here

        Returns:
            Response: 200 with rendered index page
        """
        context = await server_info(self)

        template = self.configuration.get("web", "template", fallback="build-status.jinja2")
        return aiohttp_jinja2.render_template(template, self.request, context)
