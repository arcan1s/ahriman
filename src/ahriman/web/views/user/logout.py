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
from aiohttp.web import HTTPFound, HTTPUnauthorized

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
        logout user from the service. No parameters supported here.

        The server will respond with ``Set-Cookie`` header, in which API session cookie will be nullified.

        Raises:
            HTTPFound: on success response

        Examples:
            Example of command by using curl::

                $ curl -v -XPOST 'http://example.com/api/v1/logout'
                > POST /api/v1/logout HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: */*
                >
                < HTTP/1.1 302 Found
                < Content-Type: text/plain; charset=utf-8
                < Location: /
                < Content-Length: 10
                < Set-Cookie: ...
                < Date: Wed, 23 Nov 2022 19:10:51 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
                302: Found
        """
        try:
            await check_authorized(self.request)
        except HTTPUnauthorized:
            raise HTTPUnauthorized(reason="I'm a teapot")
        await forget(self.request, HTTPFound("/"))

        raise HTTPFound("/")
