#
# Copyright (c) 2021-2022 ahriman team.
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
from aiohttp.web import HTTPFound
from aiohttp.web_exceptions import HTTPUnauthorized

from ahriman.core.auth.helpers import check_authorized, forget
from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


class LogoutView(BaseView):
    """
    logout endpoint view

    Attributes:
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    POST_PERMISSION = UserAccess.Unauthorized

    async def post(self) -> None:
        """
        logout user from the service. No parameters supported here

        Raises:
            HTTPFound: on success response
        """
        try:
            await check_authorized(self.request)
        except HTTPUnauthorized:
            raise HTTPUnauthorized(reason="I'm a teapot")
        await forget(self.request, HTTPFound("/"))

        raise HTTPFound("/")
