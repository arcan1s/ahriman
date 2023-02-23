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
from aiohttp.web import HTTPFound, HTTPMethodNotAllowed, HTTPUnauthorized

from ahriman.core.auth.helpers import remember
from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


class LoginView(BaseView):
    """
    login endpoint view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    GET_PERMISSION = POST_PERMISSION = UserAccess.Unauthorized

    async def get(self) -> None:
        """
        OAuth2 response handler

        In case if code provided it will do a request to get user email. In case if no code provided it will redirect
        to authorization url provided by OAuth client.

        The authentication session will be passed in ``Set-Cookie`` header.

        Raises:
            HTTPFound: on success response
            HTTPMethodNotAllowed: in case if method is used, but OAuth is disabled
            HTTPUnauthorized: if case of authorization error

        Examples:
            This request must not be used directly.
        """
        from ahriman.core.auth.oauth import OAuth

        oauth_provider = self.validator
        if not isinstance(oauth_provider, OAuth):  # there is actually property, but mypy does not like it anyway
            raise HTTPMethodNotAllowed(self.request.method, ["POST"])

        code = self.request.query.getone("code", default=None)
        if not code:
            raise HTTPFound(oauth_provider.get_oauth_url())

        response = HTTPFound("/")
        identity = await oauth_provider.get_oauth_username(code)
        if identity is not None and await self.validator.known_username(identity):
            await remember(self.request, response, identity)
            raise response

        raise HTTPUnauthorized()

    async def post(self) -> None:
        """
        login user to service

        either JSON body or form data must be supplied the following fields are required::

            {
                "username": "username",  # username to use for login
                "password": "pa55w0rd"   # password to use for login
            }

        The authentication session will be passed in ``Set-Cookie`` header.

        Raises:
            HTTPFound: on success response
            HTTPUnauthorized: if case of authorization error

        Examples:
            Example of command by using curl::

                $ curl -v -H 'Content-Type: application/json' 'http://example.com/api/v1/login' -d '{"username": "test", "password": "test"}'
                > POST /api/v1/login HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: */*
                > Content-Type: application/json
                > Content-Length: 40
                >
                < HTTP/1.1 302 Found
                < Content-Type: text/plain; charset=utf-8
                < Location: /
                < Content-Length: 10
                < Set-Cookie: ...
                < Date: Wed, 23 Nov 2022 17:51:27 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
                302: Found
        """
        data = await self.extract_data()
        identity = data.get("username")

        response = HTTPFound("/")
        if identity is not None and await self.validator.check_credentials(identity, data.get("password")):
            await remember(self.request, response, identity)
            raise response

        raise HTTPUnauthorized()
