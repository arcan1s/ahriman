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
from aiohttp.web import HTTPFound, HTTPMethodNotAllowed, HTTPUnauthorized, Response

from ahriman.core.auth.helpers import remember
from ahriman.models.user_access import UserAccess
from ahriman.models.user_identity import UserIdentity
from ahriman.web.views.base import BaseView


class LoginView(BaseView):
    """
    login endpoint view
    :cvar GET_PERMISSION: get permissions of self
    :cvar POST_PERMISSION: post permissions of self
    """

    GET_PERMISSION = POST_PERMISSION = UserAccess.Safe

    async def get(self) -> Response:
        """
        OAuth2 response handler

        In case if code provided it will do a request to get user email. In case if no code provided it will redirect
        to authorization url provided by OAuth client

        :return: redirect to main page
        """
        from ahriman.core.auth.oauth import OAuth

        oauth_provider = self.validator
        if not isinstance(oauth_provider, OAuth):  # there is actually property, but mypy does not like it anyway
            raise HTTPMethodNotAllowed(self.request.method, ["POST"])

        code = self.request.query.getone("code", default=None)
        if not code:
            raise HTTPFound(oauth_provider.get_oauth_url())

        response = HTTPFound("/")
        username = await oauth_provider.get_oauth_username(code)
        identity = UserIdentity.from_username(username, self.validator.max_age)
        if identity is not None and await self.validator.known_username(username):
            await remember(self.request, response, identity.to_identity())
            raise response

        raise HTTPUnauthorized()

    async def post(self) -> Response:
        """
        login user to service

        either JSON body or form data must be supplied the following fields are required:
        {
            "username": "username"  # username to use for login
            "password": "pa55w0rd"  # password to use for login
        }

        :return: redirect to main page
        """
        data = await self.extract_data()
        username = data.get("username")

        response = HTTPFound("/")
        identity = UserIdentity.from_username(username, self.validator.max_age)
        if identity is not None and await self.validator.check_credentials(username, data.get("password")):
            await remember(self.request, response, identity.to_identity())
            raise response

        raise HTTPUnauthorized()
