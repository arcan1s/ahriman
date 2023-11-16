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
import aiohttp_apispec  # type: ignore[import-untyped]

from aiohttp.web import HTTPBadRequest, HTTPFound, HTTPMethodNotAllowed, HTTPUnauthorized

from ahriman.core.auth.helpers import remember
from ahriman.models.user_access import UserAccess
from ahriman.web.schemas import ErrorSchema, LoginSchema, OAuth2Schema
from ahriman.web.views.base import BaseView


class LoginView(BaseView):
    """
    login endpoint view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    GET_PERMISSION = POST_PERMISSION = UserAccess.Unauthorized
    ROUTES = ["/api/v1/login"]

    @aiohttp_apispec.docs(
        tags=["Login"],
        summary="Login via OAuth2",
        description="Login by using OAuth2 authorization code. Only available if OAuth2 is enabled",
        responses={
            302: {"description": "Success response"},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [GET_PERMISSION]}],
    )
    @aiohttp_apispec.querystring_schema(OAuth2Schema)
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
        """
        try:
            from ahriman.core.auth.oauth import OAuth
        except ImportError:
            # no aioauth library found
            raise HTTPMethodNotAllowed(self.request.method, ["POST"])

        oauth_provider = self.validator
        if not isinstance(oauth_provider, OAuth):  # there is actually property, but mypy does not like it anyway
            raise HTTPMethodNotAllowed(self.request.method, ["POST"])

        code = self.request.query.get("code")
        if not code:
            raise HTTPFound(oauth_provider.get_oauth_url())

        response = HTTPFound("/")
        identity = await oauth_provider.get_oauth_username(code)
        if identity is not None and await self.validator.known_username(identity):
            await remember(self.request, response, identity)
            raise response

        raise HTTPUnauthorized

    @aiohttp_apispec.docs(
        tags=["Login"],
        summary="Login via basic authorization",
        description="Login by using username and password",
        responses={
            302: {"description": "Success response"},
            400: {"description": "Bad data is supplied", "schema": ErrorSchema},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [POST_PERMISSION]}],
    )
    @aiohttp_apispec.json_schema(LoginSchema)
    async def post(self) -> None:
        """
        login user to service. The authentication session will be passed in ``Set-Cookie`` header.

        Raises:
            HTTPFound: on success response
            HTTPUnauthorized: if case of authorization error
        """
        try:
            data = await self.request.json()
            identity = data["username"]
            password = data["password"]
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        response = HTTPFound("/")
        if await self.validator.check_credentials(identity, password):
            await remember(self.request, response, identity)
            raise response

        raise HTTPUnauthorized
