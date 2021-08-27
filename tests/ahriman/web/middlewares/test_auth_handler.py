from aiohttp import web
from pytest_mock import MockerFixture
from typing import Any
from unittest.mock import AsyncMock

from ahriman.core.configuration import Configuration
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess
from ahriman.web.middlewares.auth_handler import auth_handler, AuthorizationPolicy, setup_auth


async def test_authorized_userid(authorization_policy: AuthorizationPolicy, user: User) -> None:
    """
    must return authorized user id
    """
    assert await authorization_policy.authorized_userid(user.username) == user.username
    assert await authorization_policy.authorized_userid("some random name") is None


async def test_permits(authorization_policy: AuthorizationPolicy, user: User, mocker: MockerFixture) -> None:
    """
    must call validator check
    """
    safe_request_mock = mocker.patch("ahriman.core.auth.Auth.is_safe_request", return_value=False)
    verify_access_mock = mocker.patch("ahriman.core.auth.Auth.verify_access", return_value=True)

    assert await authorization_policy.permits(user.username, user.access, "/endpoint")
    safe_request_mock.assert_called_with("/endpoint")
    verify_access_mock.assert_called_with(user.username, user.access)


async def test_permits_safe(authorization_policy: AuthorizationPolicy, user: User, mocker: MockerFixture) -> None:
    """
    must call validator check
    """
    safe_request_mock = mocker.patch("ahriman.core.auth.Auth.is_safe_request", return_value=True)
    verify_access_mock = mocker.patch("ahriman.core.auth.Auth.verify_access")

    assert await authorization_policy.permits(user.username, user.access, "/endpoint")
    safe_request_mock.assert_called_with("/endpoint")
    verify_access_mock.assert_not_called()


async def test_auth_handler_api(aiohttp_request: Any, mocker: MockerFixture) -> None:
    """
    must ask for status permission for api calls
    """
    aiohttp_request = aiohttp_request._replace(path="/api")
    request_handler = AsyncMock()
    check_permission_mock = mocker.patch("aiohttp_security.check_permission")

    handler = auth_handler()
    await handler(aiohttp_request, request_handler)
    check_permission_mock.assert_called_with(aiohttp_request, UserAccess.Status, aiohttp_request.path)


async def test_auth_handler_api_post(aiohttp_request: Any, mocker: MockerFixture) -> None:
    """
    must ask for status permission for api calls with POST
    """
    aiohttp_request = aiohttp_request._replace(path="/api", method="POST")
    request_handler = AsyncMock()
    check_permission_mock = mocker.patch("aiohttp_security.check_permission")

    handler = auth_handler()
    await handler(aiohttp_request, request_handler)
    check_permission_mock.assert_called_with(aiohttp_request, UserAccess.Status, aiohttp_request.path)


async def test_auth_handler_read(aiohttp_request: Any, mocker: MockerFixture) -> None:
    """
    must ask for read permission for api calls with GET
    """
    for method in ("GET", "HEAD", "OPTIONS"):
        aiohttp_request = aiohttp_request._replace(method=method)
        request_handler = AsyncMock()
        check_permission_mock = mocker.patch("aiohttp_security.check_permission")

        handler = auth_handler()
        await handler(aiohttp_request, request_handler)
        check_permission_mock.assert_called_with(aiohttp_request, UserAccess.Read, aiohttp_request.path)


async def test_auth_handler_write(aiohttp_request: Any, mocker: MockerFixture) -> None:
    """
    must ask for read permission for api calls with POST
    """
    for method in ("CONNECT", "DELETE", "PATCH", "POST", "PUT", "TRACE"):
        aiohttp_request = aiohttp_request._replace(method=method)
        request_handler = AsyncMock()
        check_permission_mock = mocker.patch("aiohttp_security.check_permission")

        handler = auth_handler()
        await handler(aiohttp_request, request_handler)
        check_permission_mock.assert_called_with(aiohttp_request, UserAccess.Write, aiohttp_request.path)


def test_setup_auth(application: web.Application, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must setup authorization
    """
    aiohttp_security_setup_mock = mocker.patch("aiohttp_security.setup")
    application = setup_auth(application, configuration)
    assert application.get("validator") is not None
    aiohttp_security_setup_mock.assert_called_once()
