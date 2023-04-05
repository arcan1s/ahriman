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

from aiohttp.web import Application, Request, StaticResource, StreamResponse, middleware
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet
from typing import Optional

from ahriman.core.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.models.user_access import UserAccess
from ahriman.web.middlewares import HandlerType, MiddlewareType


__all__ = ["setup_auth"]


class _AuthorizationPolicy(aiohttp_security.AbstractAuthorizationPolicy):
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
        return identity if await self.validator.known_username(identity) else None

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
        return await self.validator.verify_access(identity, permission, context)


def _auth_handler(allow_read_only: bool) -> MiddlewareType:
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


def _cookie_secret_key(configuration: Configuration) -> fernet.Fernet:
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


def setup_auth(application: Application, configuration: Configuration, validator: Auth) -> Application:
    """
    setup authorization policies for the application

    Args:
        application(Application): web application instance
        configuration(Configuration): configuration instance
        validator(Auth): authorization module instance

    Returns:
        Application: configured web application
    """
    secret_key = _cookie_secret_key(configuration)
    storage = EncryptedCookieStorage(secret_key, cookie_name="API_SESSION", max_age=validator.max_age)
    setup_session(application, storage)

    authorization_policy = _AuthorizationPolicy(validator)
    identity_policy = aiohttp_security.SessionIdentityPolicy()

    aiohttp_security.setup(application, identity_policy, authorization_policy)
    application.middlewares.append(_auth_handler(validator.allow_read_only))

    return application
