#
# Copyright (c) 2021-2023 ahriman team.
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

from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


class DocsView(BaseView):
    """
    api docs view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
    """

    GET_PERMISSION = UserAccess.Unauthorized

    @aiohttp_jinja2.template("api.jinja2")
    async def get(self) -> Dict[str, Any]:
        """
        return static docs html

        Returns:
            Dict[str, Any]: parameters for jinja template
        """
        return {}
