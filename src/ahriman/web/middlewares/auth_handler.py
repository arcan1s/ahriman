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
from aiohttp import web
from aiohttp.web import middleware, Request
from aiohttp.web_response import StreamResponse
from aiohttp_security import setup as setup_security  # type: ignore
from aiohttp_security import AbstractAuthorizationPolicy, SessionIdentityPolicy, check_permission
from typing import Optional

from ahriman.core.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.models.user_access import UserAccess
from ahriman.web.middlewares import HandlerType, MiddlewareType


class AuthorizationPolicy(AbstractAuthorizationPolicy):  # type: ignore
    """
    authorization policy implementation
    :ivar validator: validator instance
    """

    def __init__(self, configuration: Configuration) -> None:
        """
        default constructor
        :param configuration: configuration instance
        """
        self.validator = Auth(configuration)

    async def authorized_userid(self, identity: str) -> Optional[str]:
        """
        retrieve authorized username
        :param identity: username
        :return: user identity (username) in case if user exists and None otherwise
        """
        return identity if identity in self.validator.users else None

    async def permits(self, identity: str, permission: UserAccess, context: Optional[str] = None) -> bool:
        """
        check user permissions
        :param identity: username
        :param permission: requested permission level
        :param context: URI request path
        :return: True in case if user is allowed to perform this request and False otherwise
        """
        if self.validator.is_safe_request(context):
            return True
        return self.validator.verify_access(identity, permission)


def auth_handler() -> MiddlewareType:
    """
    authorization and authentication middleware
    :return: built middleware
    """
    @middleware
    async def handle(request: Request, handler: HandlerType) -> StreamResponse:
        if request.path.startswith("/api"):
            permission = UserAccess.Status
        elif request.method in ("HEAD", "GET", "OPTIONS"):
            permission = UserAccess.Read
        else:
            permission = UserAccess.Write
        await check_permission(request, permission, request.path)

        return await handler(request)

    return handle


def setup_auth(application: web.Application, configuration: Configuration) -> web.Application:
    """
    setup authorization policies for the application
    :param application: web application instance
    :param configuration: configuration instance
    :return: configured web application
    """
    authorization_policy = AuthorizationPolicy(configuration)
    identity_policy = SessionIdentityPolicy()

    application["validator"] = authorization_policy.validator
    setup_security(application, identity_policy, authorization_policy)
    application.middlewares.append(auth_handler())

    return application
