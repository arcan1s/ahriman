import pytest

from aiohttp import web
from pytest_mock import MockerFixture
from unittest.mock import AsyncMock, MagicMock

from ahriman.core.auth.auth import Auth
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


async def test_permits(authorization_policy: AuthorizationPolicy, user: User) -> None:
    """
    must call validator check
    """
    authorization_policy.validator = MagicMock()
    authorization_policy.validator.verify_access.return_value = True

    assert await authorization_policy.permits(user.username, user.access, "/endpoint")
    authorization_policy.validator.verify_access.assert_called_with(user.username, user.access, "/endpoint")


async def test_auth_handler_api(auth: Auth, mocker: MockerFixture) -> None:
    """
    must ask for status permission for api calls
    """
    aiohttp_request = pytest.helpers.request("", "/status-api", "GET")
    request_handler = AsyncMock()
    mocker.patch("ahriman.core.auth.auth.Auth.is_safe_request", return_value=False)
    check_permission_mock = mocker.patch("aiohttp_security.check_permission")

    handler = auth_handler(auth)
    await handler(aiohttp_request, request_handler)
    check_permission_mock.assert_called_with(aiohttp_request, UserAccess.Read, aiohttp_request.path)


async def test_auth_handler_api_post(auth: Auth, mocker: MockerFixture) -> None:
    """
    must ask for status permission for api calls with POST
    """
    aiohttp_request = pytest.helpers.request("", "/status-api", "POST")
    request_handler = AsyncMock()
    mocker.patch("ahriman.core.auth.auth.Auth.is_safe_request", return_value=False)
    check_permission_mock = mocker.patch("aiohttp_security.check_permission")

    handler = auth_handler(auth)
    await handler(aiohttp_request, request_handler)
    check_permission_mock.assert_called_with(aiohttp_request, UserAccess.Write, aiohttp_request.path)


async def test_auth_handler_read(auth: Auth, mocker: MockerFixture) -> None:
    """
    must ask for read permission for api calls with GET
    """
    for method in ("GET", "HEAD", "OPTIONS"):
        aiohttp_request = pytest.helpers.request("", "", method)
        request_handler = AsyncMock()
        mocker.patch("ahriman.core.auth.auth.Auth.is_safe_request", return_value=False)
        check_permission_mock = mocker.patch("aiohttp_security.check_permission")

        handler = auth_handler(auth)
        await handler(aiohttp_request, request_handler)
        check_permission_mock.assert_called_with(aiohttp_request, UserAccess.Read, aiohttp_request.path)


async def test_auth_handler_write(auth: Auth, mocker: MockerFixture) -> None:
    """
    must ask for read permission for api calls with POST
    """
    for method in ("CONNECT", "DELETE", "PATCH", "POST", "PUT", "TRACE"):
        aiohttp_request = pytest.helpers.request("", "", method)
        request_handler = AsyncMock()
        mocker.patch("ahriman.core.auth.auth.Auth.is_safe_request", return_value=False)
        check_permission_mock = mocker.patch("aiohttp_security.check_permission")

        handler = auth_handler(auth)
        await handler(aiohttp_request, request_handler)
        check_permission_mock.assert_called_with(aiohttp_request, UserAccess.Write, aiohttp_request.path)


def test_setup_auth(application_with_auth: web.Application, auth: Auth, mocker: MockerFixture) -> None:
    """
    must setup authorization
    """
    aiohttp_security_setup_mock = mocker.patch("aiohttp_security.setup")
    application = setup_auth(application_with_auth, auth)
    assert application.get("validator") is not None
    aiohttp_security_setup_mock.assert_called_once()
