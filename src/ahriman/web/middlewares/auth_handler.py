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
import aiohttp_security  # type: ignore
import base64

from aiohttp import web
from aiohttp.web import middleware, Request
from aiohttp.web_response import StreamResponse
from aiohttp_session import setup as setup_session  # type: ignore
from aiohttp_session.cookie_storage import EncryptedCookieStorage  # type: ignore
from cryptography import fernet
from typing import Optional

from ahriman.core.auth.auth import Auth
from ahriman.models.user_access import UserAccess
from ahriman.models.user_identity import UserIdentity
from ahriman.web.middlewares import HandlerType, MiddlewareType


class AuthorizationPolicy(aiohttp_security.AbstractAuthorizationPolicy):  # type: ignore
    """
    authorization policy implementation
    :ivar validator: validator instance
    """

    def __init__(self, validator: Auth) -> None:
        """
        default constructor
        :param validator: authorization module instance
        """
        self.validator = validator

    async def authorized_userid(self, identity: str) -> Optional[str]:
        """
        retrieve authenticated username
        :param identity: username
        :return: user identity (username) in case if user exists and None otherwise
        """
        user = UserIdentity.from_identity(identity)
        if user is None:
            return None
        return user.username if await self.validator.known_username(user.username) else None

    async def permits(self, identity: str, permission: UserAccess, context: Optional[str] = None) -> bool:
        """
        check user permissions
        :param identity: username
        :param permission: requested permission level
        :param context: URI request path
        :return: True in case if user is allowed to perform this request and False otherwise
        """
        user = UserIdentity.from_identity(identity)
        if user is None:
            return False
        return await self.validator.verify_access(user.username, permission, context)


def auth_handler(validator: Auth) -> MiddlewareType:
    """
    authorization and authentication middleware
    :param validator: authorization module instance
    :return: built middleware
    """
    @middleware
    async def handle(request: Request, handler: HandlerType) -> StreamResponse:
        if request.method in ("GET", "HEAD", "OPTIONS"):
            permission = UserAccess.Read
        else:
            permission = UserAccess.Write

        if not await validator.is_safe_request(request.path, permission):
            await aiohttp_security.check_permission(request, permission, request.path)

        return await handler(request)

    return handle


def setup_auth(application: web.Application, validator: Auth) -> web.Application:
    """
    setup authorization policies for the application
    :param application: web application instance
    :param validator: authorization module instance
    :return: configured web application
    """
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    storage = EncryptedCookieStorage(secret_key, cookie_name="API_SESSION", max_age=validator.max_age)
    setup_session(application, storage)

    authorization_policy = AuthorizationPolicy(validator)
    identity_policy = aiohttp_security.SessionIdentityPolicy()

    aiohttp_security.setup(application, identity_policy, authorization_policy)
    application.middlewares.append(auth_handler(validator))

    return application
