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

from typing import Any

from ahriman.core.configuration import Configuration
from ahriman.models.user_access import UserAccess
from ahriman.web.apispec import aiohttp_apispec
from ahriman.web.views.base import BaseView


class DocsView(BaseView):
    """
    api docs view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
    """

    GET_PERMISSION = UserAccess.Unauthorized
    ROUTES = ["/api-docs"]

    @classmethod
    def routes(cls, configuration: Configuration) -> list[str]:
        """
        extract routes list for the view

        Args:
            configuration(Configuration): configuration instance

        Returns:
            list[str]: list of routes defined for the view. By default, it tries to read :attr:`ROUTES` option if set
            and returns empty list otherwise
        """
        if aiohttp_apispec is None:
            return []
        return cls.ROUTES

    @aiohttp_jinja2.template("api.jinja2")
    async def get(self) -> dict[str, Any]:
        """
        return static docs html

        Returns:
            dict[str, Any]: parameters for jinja template
        """
        return {}
