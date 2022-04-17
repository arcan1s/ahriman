import pytest

from aiohttp import web
from pytest_mock import MockerFixture
from unittest.mock import AsyncMock

from ahriman.core.auth.auth import Auth
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess
from ahriman.models.user_identity import UserIdentity
from ahriman.web.middlewares.auth_handler import auth_handler, AuthorizationPolicy, setup_auth


def _identity(username: str) -> str:
    """
    generate identity from user

    Args:
        username(str): name of the user

    Returns:
        str: user identity string
    """
    return f"{username} {UserIdentity.expire_when(60)}"


async def test_authorized_userid(authorization_policy: AuthorizationPolicy, user: User, mocker: MockerFixture) -> None:
    """
    must return authorized user id
    """
    mocker.patch("ahriman.core.database.sqlite.SQLite.user_get", return_value=user)
    assert await authorization_policy.authorized_userid(_identity(user.username)) == user.username


async def test_authorized_userid_unknown(authorization_policy: AuthorizationPolicy, user: User) -> None:
    """
    must not allow unknown user id for authorization
    """
    assert await authorization_policy.authorized_userid(_identity("somerandomname")) is None
    assert await authorization_policy.authorized_userid("somerandomname") is None


async def test_permits(authorization_policy: AuthorizationPolicy, user: User) -> None:
    """
    must call validator check
    """
    authorization_policy.validator = AsyncMock()
    authorization_policy.validator.verify_access.side_effect = lambda username, *args: username == user.username

    assert await authorization_policy.permits(_identity(user.username), user.access, "/endpoint")
    authorization_policy.validator.verify_access.assert_called_once_with(user.username, user.access, "/endpoint")

    assert not await authorization_policy.permits(_identity("somerandomname"), user.access, "/endpoint")
    assert not await authorization_policy.permits(user.username, user.access, "/endpoint")


async def test_auth_handler_api(mocker: MockerFixture) -> None:
    """
    must ask for status permission for api calls
    """
    aiohttp_request = pytest.helpers.request("", "/status-api", "GET")
    request_handler = AsyncMock()
    request_handler.get_permission.return_value = UserAccess.Read
    check_permission_mock = mocker.patch("aiohttp_security.check_permission")

    handler = auth_handler()
    await handler(aiohttp_request, request_handler)
    check_permission_mock.assert_called_once_with(aiohttp_request, UserAccess.Read, aiohttp_request.path)


async def test_auth_handler_api_no_method(mocker: MockerFixture) -> None:
    """
    must ask for write permission if handler does not have get_permission method
    """
    aiohttp_request = pytest.helpers.request("", "/status-api", "GET")
    request_handler = AsyncMock()
    request_handler.get_permission = None
    check_permission_mock = mocker.patch("aiohttp_security.check_permission")

    handler = auth_handler()
    await handler(aiohttp_request, request_handler)
    check_permission_mock.assert_called_once_with(aiohttp_request, UserAccess.Write, aiohttp_request.path)


async def test_auth_handler_api_post(mocker: MockerFixture) -> None:
    """
    must ask for status permission for api calls with POST
    """
    aiohttp_request = pytest.helpers.request("", "/status-api", "POST")
    request_handler = AsyncMock()
    request_handler.get_permission.return_value = UserAccess.Write
    check_permission_mock = mocker.patch("aiohttp_security.check_permission")

    handler = auth_handler()
    await handler(aiohttp_request, request_handler)
    check_permission_mock.assert_called_once_with(aiohttp_request, UserAccess.Write, aiohttp_request.path)


async def test_auth_handler_read(mocker: MockerFixture) -> None:
    """
    must ask for read permission for api calls with GET
    """
    for method in ("GET", "HEAD", "OPTIONS"):
        aiohttp_request = pytest.helpers.request("", "", method)
        request_handler = AsyncMock()
        request_handler.get_permission.return_value = UserAccess.Read
        check_permission_mock = mocker.patch("aiohttp_security.check_permission")

        handler = auth_handler()
        await handler(aiohttp_request, request_handler)
        check_permission_mock.assert_called_once_with(aiohttp_request, UserAccess.Read, aiohttp_request.path)


async def test_auth_handler_write(mocker: MockerFixture) -> None:
    """
    must ask for read permission for api calls with POST
    """
    for method in ("CONNECT", "DELETE", "PATCH", "POST", "PUT", "TRACE"):
        aiohttp_request = pytest.helpers.request("", "", method)
        request_handler = AsyncMock()
        request_handler.get_permission.return_value = UserAccess.Write
        check_permission_mock = mocker.patch("aiohttp_security.check_permission")

        handler = auth_handler()
        await handler(aiohttp_request, request_handler)
        check_permission_mock.assert_called_once_with(aiohttp_request, UserAccess.Write, aiohttp_request.path)


def test_setup_auth(application_with_auth: web.Application, auth: Auth, mocker: MockerFixture) -> None:
    """
    must setup authorization
    """
    setup_mock = mocker.patch("aiohttp_security.setup")
    application = setup_auth(application_with_auth, auth)
    assert application.get("validator") is not None
    setup_mock.assert_called_once_with(application_with_auth, pytest.helpers.anyvar(int), pytest.helpers.anyvar(int))
