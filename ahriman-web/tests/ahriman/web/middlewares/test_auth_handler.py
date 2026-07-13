import pytest
import socket

from aiohttp.test_utils import TestClient
from aiohttp.web import Application
from cryptography import fernet
from pytest_mock import MockerFixture
from unittest.mock import AsyncMock, call as MockCall

from ahriman.core.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess
from ahriman.web.keys import AuthKey
from ahriman.web.middlewares.auth_handler import _AuthorizationPolicy, _auth_handler, _cookie_secret_key, setup_auth


async def test_authorized_userid(authorization_policy: _AuthorizationPolicy, user: User, mocker: MockerFixture) -> None:
    """
    must return authorized user id
    """
    mocker.patch("ahriman.core.database.SQLite.user_get", return_value=user)
    assert await authorization_policy.authorized_userid(user.username) == user.username


async def test_authorized_userid_unknown(authorization_policy: _AuthorizationPolicy) -> None:
    """
    must not allow unknown user id for authorization
    """
    assert await authorization_policy.authorized_userid("somerandomname") is None
    assert await authorization_policy.authorized_userid("somerandomname") is None


async def test_permits(authorization_policy: _AuthorizationPolicy, user: User) -> None:
    """
    must call validator check
    """
    authorization_policy.validator = AsyncMock()
    authorization_policy.validator.verify_access.side_effect = lambda username, *args: username == user.username

    assert await authorization_policy.permits(user.username, user.access, "/endpoint")
    assert not await authorization_policy.permits("somerandomname", user.access, "/endpoint")
    assert not await authorization_policy.permits(None, user.access, "/endpoint")
    assert not await authorization_policy.permits(user.username, "random", "/endpoint")
    assert not await authorization_policy.permits(None, BuildStatusEnum.Building, "/endpoint")

    authorization_policy.validator.verify_access.assert_has_calls([
        MockCall(user.username, user.access, "/endpoint"),
        MockCall("somerandomname", user.access, "/endpoint"),
    ])


async def test_auth_handler_unix_socket(mocker: MockerFixture) -> None:
    """
    must allow calls via unix sockets
    """
    aiohttp_request = pytest.helpers.request(
        "", "/api/v1/status", "GET", extra={"socket": socket.socket(socket.AF_UNIX)})
    request_handler = AsyncMock()
    request_handler.get_permission.return_value = UserAccess.Full
    check_permission_mock = mocker.patch("aiohttp_security.check_permission")

    handler = _auth_handler(allow_read_only=False)
    await handler(aiohttp_request, request_handler)
    check_permission_mock.assert_not_called()


async def test_auth_handler_api(mocker: MockerFixture) -> None:
    """
    must ask for status permission for api calls
    """
    aiohttp_request = pytest.helpers.request("", "/api/v1/status", "GET")
    request_handler = AsyncMock()
    request_handler.get_permission.return_value = UserAccess.Read
    check_permission_mock = mocker.patch("aiohttp_security.check_permission")

    handler = _auth_handler(allow_read_only=False)
    await handler(aiohttp_request, request_handler)
    check_permission_mock.assert_called_once_with(aiohttp_request, UserAccess.Read, aiohttp_request.path)


async def test_auth_handler_static(client_with_auth: TestClient, mocker: MockerFixture) -> None:
    """
    must allow static calls
    """
    check_permission_mock = mocker.patch("aiohttp_security.check_permission")
    await client_with_auth.get("/static/favicon.ico")
    check_permission_mock.assert_not_called()


async def test_auth_handler_unauthorized(client_with_auth: TestClient, mocker: MockerFixture) -> None:
    """
    must allow pages with unauthorized access
    """
    check_permission_mock = mocker.patch("aiohttp_security.check_permission")
    await client_with_auth.get("/")
    check_permission_mock.assert_not_called()


async def test_auth_handler_allow_read_only(mocker: MockerFixture) -> None:
    """
    must allow pages with allow read only flag
    """
    aiohttp_request = pytest.helpers.request("", "/api/v1/status", "GET")
    request_handler = AsyncMock()
    request_handler.get_permission.return_value = UserAccess.Read
    check_permission_mock = mocker.patch("aiohttp_security.check_permission")

    handler = _auth_handler(allow_read_only=True)
    await handler(aiohttp_request, request_handler)
    check_permission_mock.assert_not_called()


async def test_auth_handler_api_no_method(mocker: MockerFixture) -> None:
    """
    must ask for write permission if handler does not have get_permission method
    """
    aiohttp_request = pytest.helpers.request("", "/api/v1/status", "GET")
    request_handler = AsyncMock()
    request_handler.get_permission = None
    check_permission_mock = mocker.patch("aiohttp_security.check_permission")

    handler = _auth_handler(allow_read_only=False)
    await handler(aiohttp_request, request_handler)
    check_permission_mock.assert_called_once_with(aiohttp_request, UserAccess.Full, aiohttp_request.path)


async def test_auth_handler_api_post(mocker: MockerFixture) -> None:
    """
    must ask for status permission for api calls with POST
    """
    aiohttp_request = pytest.helpers.request("", "/api/v1/status", "POST")
    request_handler = AsyncMock()
    request_handler.get_permission.return_value = UserAccess.Full
    check_permission_mock = mocker.patch("aiohttp_security.check_permission")

    handler = _auth_handler(allow_read_only=False)
    await handler(aiohttp_request, request_handler)
    check_permission_mock.assert_called_once_with(aiohttp_request, UserAccess.Full, aiohttp_request.path)


async def test_auth_handler_read(mocker: MockerFixture) -> None:
    """
    must ask for read permission for api calls with GET
    """
    for method in ("GET", "HEAD", "OPTIONS"):
        aiohttp_request = pytest.helpers.request("", "", method)
        request_handler = AsyncMock()
        request_handler.get_permission.return_value = UserAccess.Read
        check_permission_mock = mocker.patch("aiohttp_security.check_permission")

        handler = _auth_handler(allow_read_only=False)
        await handler(aiohttp_request, request_handler)
        check_permission_mock.assert_called_once_with(aiohttp_request, UserAccess.Read, aiohttp_request.path)


async def test_auth_handler_write(mocker: MockerFixture) -> None:
    """
    must ask for read permission for api calls with POST
    """
    for method in ("CONNECT", "DELETE", "PATCH", "POST", "PUT", "TRACE"):
        aiohttp_request = pytest.helpers.request("", "", method)
        request_handler = AsyncMock()
        request_handler.get_permission.return_value = UserAccess.Full
        check_permission_mock = mocker.patch("aiohttp_security.check_permission")

        handler = _auth_handler(allow_read_only=False)
        await handler(aiohttp_request, request_handler)
        check_permission_mock.assert_called_once_with(aiohttp_request, UserAccess.Full, aiohttp_request.path)


def test_cookie_secret_key(configuration: Configuration) -> None:
    """
    must generate fernet key
    """
    secret_key = _cookie_secret_key(configuration)
    assert isinstance(secret_key, fernet.Fernet)


def test_cookie_secret_key_cached(configuration: Configuration) -> None:
    """
    must use cookie key as set by configuration
    """
    configuration.set_option("auth", "cookie_secret_key", fernet.Fernet.generate_key().decode("utf8"))
    assert _cookie_secret_key(configuration) is not None


def test_setup_auth(application_with_auth: Application, configuration: Configuration, auth: Auth,
                    mocker: MockerFixture) -> None:
    """
    must set up authorization
    """
    setup_mock = mocker.patch("aiohttp_security.setup")
    application = setup_auth(application_with_auth, configuration, auth)
    assert application.get(AuthKey) is not None
    setup_mock.assert_called_once_with(application_with_auth, pytest.helpers.anyvar(int), pytest.helpers.anyvar(int))
