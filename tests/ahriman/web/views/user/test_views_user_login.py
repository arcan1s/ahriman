import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.auth.oauth import OAuth
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess
from ahriman.web.views.user.login import LoginView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET", "POST"):
        request = pytest.helpers.request("", "", method)
        assert await LoginView.get_permission(request) == UserAccess.Safe


async def test_get_default_validator(client_with_auth: TestClient) -> None:
    """
    must return 405 in case if no OAuth enabled
    """
    get_response = await client_with_auth.get("/user-api/v1/login")
    assert get_response.status == 405


async def test_get_redirect_to_oauth(client_with_auth: TestClient) -> None:
    """
    must redirect to OAuth service provider in case if no code is supplied
    """
    oauth = client_with_auth.app["validator"] = MagicMock(spec=OAuth)
    oauth.get_oauth_url.return_value = "https://httpbin.org"

    get_response = await client_with_auth.get("/user-api/v1/login")
    assert get_response.ok
    oauth.get_oauth_url.assert_called_once_with()


async def test_get_redirect_to_oauth_empty_code(client_with_auth: TestClient) -> None:
    """
    must redirect to OAuth service provider in case if empty code is supplied
    """
    oauth = client_with_auth.app["validator"] = MagicMock(spec=OAuth)
    oauth.get_oauth_url.return_value = "https://httpbin.org"

    get_response = await client_with_auth.get("/user-api/v1/login", params={"code": ""})
    assert get_response.ok
    oauth.get_oauth_url.assert_called_once_with()


async def test_get(client_with_auth: TestClient, mocker: MockerFixture) -> None:
    """
    must login user correctly from OAuth
    """
    oauth = client_with_auth.app["validator"] = MagicMock(spec=OAuth)
    oauth.get_oauth_username.return_value = "user"
    oauth.known_username.return_value = True
    oauth.enabled = False  # lol
    oauth.max_age = 60
    remember_mock = mocker.patch("aiohttp_security.remember")

    get_response = await client_with_auth.get("/user-api/v1/login", params={"code": "code"})

    assert get_response.ok
    oauth.get_oauth_username.assert_called_once_with("code")
    oauth.known_username.assert_called_once_with("user")
    remember_mock.assert_called_once_with(
        pytest.helpers.anyvar(int), pytest.helpers.anyvar(int), pytest.helpers.anyvar(int))


async def test_get_unauthorized(client_with_auth: TestClient, mocker: MockerFixture) -> None:
    """
    must return unauthorized from OAuth
    """
    oauth = client_with_auth.app["validator"] = MagicMock(spec=OAuth)
    oauth.known_username.return_value = False
    oauth.max_age = 60
    remember_mock = mocker.patch("aiohttp_security.remember")

    get_response = await client_with_auth.get("/user-api/v1/login", params={"code": "code"})

    assert get_response.status == 401
    remember_mock.assert_not_called()


async def test_post(client_with_auth: TestClient, user: User, mocker: MockerFixture) -> None:
    """
    must login user correctly
    """
    payload = {"username": user.username, "password": user.password}
    remember_mock = mocker.patch("aiohttp_security.remember")

    post_response = await client_with_auth.post("/user-api/v1/login", json=payload)
    assert post_response.ok

    post_response = await client_with_auth.post("/user-api/v1/login", data=payload)
    assert post_response.ok

    remember_mock.assert_called()


async def test_post_skip(client: TestClient, user: User) -> None:
    """
    must process if no auth configured
    """
    payload = {"username": user.username, "password": user.password}
    post_response = await client.post("/user-api/v1/login", json=payload)
    assert post_response.ok


async def test_post_unauthorized(client_with_auth: TestClient, user: User, mocker: MockerFixture) -> None:
    """
    must return unauthorized on invalid auth
    """
    payload = {"username": user.username, "password": ""}
    remember_mock = mocker.patch("aiohttp_security.remember")

    post_response = await client_with_auth.post("/user-api/v1/login", json=payload)
    assert post_response.status == 401
    remember_mock.assert_not_called()
