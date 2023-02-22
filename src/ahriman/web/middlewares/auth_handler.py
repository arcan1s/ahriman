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
import aiohttp_security  # type: ignore
import socket
import types

from aiohttp import web
from aiohttp.web import middleware, Request
from aiohttp.web_response import StreamResponse
from aiohttp.web_urldispatcher import StaticResource
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet
from typing import Optional

from ahriman.core.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.models.user_access import UserAccess
from ahriman.models.user_identity import UserIdentity
from ahriman.web.middlewares import HandlerType, MiddlewareType


__all__ = ["AuthorizationPolicy", "auth_handler", "cookie_secret_key", "setup_auth"]


class AuthorizationPolicy(aiohttp_security.AbstractAuthorizationPolicy):  # type: ignore
    """
    authorization policy implementation

    Attributes:
        validator(Auth): validator instance
    """

    def __init__(self, validator: Auth) -> None:
        """
        default constructor

        Args:
            validator(Auth): authorization module instance
        """
        self.validator = validator

    async def authorized_userid(self, identity: str) -> Optional[str]:
        """
        retrieve authenticated username

        Args:
            identity(str): username

        Returns:
            Optional[str]: user identity (username) in case if user exists and None otherwise
        """
        user = UserIdentity.from_identity(identity)
        if user is None:
            return None
        return user.username if await self.validator.known_username(user.username) else None

    async def permits(self, identity: str, permission: UserAccess, context: Optional[str] = None) -> bool:
        """
        check user permissions

        Args:
            identity(str): username
            permission(UserAccess): requested permission level
            context(Optional[str], optional): URI request path (Default value = None)

        Returns:
            bool: True in case if user is allowed to perform this request and False otherwise
        """
        user = UserIdentity.from_identity(identity)
        if user is None:
            return False
        return await self.validator.verify_access(user.username, permission, context)


def auth_handler(allow_read_only: bool) -> MiddlewareType:
    """
    authorization and authentication middleware

    Args:
        allow_read_only: allow

    Returns:
        MiddlewareType: built middleware
    """
    @middleware
    async def handle(request: Request, handler: HandlerType) -> StreamResponse:
        if (unix_socket := request.get_extra_info("socket")) is not None and unix_socket.family == socket.AF_UNIX:
            # special case for unix sockets. We need to extract socket which is used for the request
            # and check its address family
            permission = UserAccess.Unauthorized
        elif (permission_method := getattr(handler, "get_permission", None)) is not None:
            permission = await permission_method(request)
        elif isinstance(handler, types.MethodType):  # additional wrapper for static resources
            handler_instance = getattr(handler, "__self__", None)
            permission = UserAccess.Unauthorized if isinstance(handler_instance, StaticResource) else UserAccess.Full
        else:
            permission = UserAccess.Full
        if permission == UserAccess.Unauthorized:  # explicit if elif else for better code coverage
            pass
        elif allow_read_only and UserAccess.Read.permits(permission):
            pass
        else:
            await aiohttp_security.check_permission(request, permission, request.path)

        return await handler(request)

    return handle


def cookie_secret_key(configuration: Configuration) -> fernet.Fernet:
    """
    extract cookie secret key from configuration if set or generate new one

    Args:
        configuration(Configuration): configuration instance

    Returns:
        fernet.Fernet: fernet key instance
    """
    if (secret_key := configuration.get("auth", "cookie_secret_key", fallback=None)) is not None:
        return fernet.Fernet(secret_key)

    secret_key = fernet.Fernet.generate_key()
    return fernet.Fernet(secret_key)


def setup_auth(application: web.Application, configuration: Configuration, validator: Auth) -> web.Application:
    """
    setup authorization policies for the application

    Args:
        application(web.Application): web application instance
        configuration(Configuration): configuration instance
        validator(Auth): authorization module instance

    Returns:
        web.Application: configured web application
    """
    secret_key = cookie_secret_key(configuration)
    storage = EncryptedCookieStorage(secret_key, cookie_name="API_SESSION", max_age=validator.max_age)
    setup_session(application, storage)

    authorization_policy = AuthorizationPolicy(validator)
    identity_policy = aiohttp_security.SessionIdentityPolicy()

    aiohttp_security.setup(application, identity_policy, authorization_policy)
    application.middlewares.append(auth_handler(validator.allow_read_only))

    return application
