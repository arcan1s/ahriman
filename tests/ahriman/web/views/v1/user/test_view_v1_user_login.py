import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.user import User
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.user.login import LoginView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET", "POST"):
        request = pytest.helpers.request("", "", method)
        assert await LoginView.get_permission(request) == UserAccess.Unauthorized


def test_routes() -> None:
    """
    must return correct routes
    """
    assert LoginView.ROUTES == ["/api/v1/login"]


async def test_get_default_validator(client_with_auth: TestClient) -> None:
    """
    must return 405 in case if no OAuth enabled
    """
    response = await client_with_auth.get("/api/v1/login")
    assert response.status == 405


async def test_get_import_error(client_with_auth: TestClient, mocker: MockerFixture) -> None:
    """
    must return 405 on import error
    """
    pytest.helpers.import_error("ahriman.core.auth.oauth", ["OAuth"], mocker)
    response = await client_with_auth.get("/api/v1/login")
    assert response.status == 405


async def test_get_redirect_to_oauth(client_with_oauth_auth: TestClient) -> None:
    """
    must redirect to OAuth service provider in case if no code is supplied
    """
    oauth = client_with_oauth_auth.app["validator"]
    oauth.get_oauth_url.return_value = "http://localhost"
    request_schema = pytest.helpers.schema_request(LoginView.get, location="querystring")

    payload = {}
    assert not request_schema.validate(payload)
    response = await client_with_oauth_auth.get("/api/v1/login", params=payload, allow_redirects=False)
    assert response.ok
    oauth.get_oauth_url.assert_called_once_with()


async def test_get_redirect_to_oauth_empty_code(client_with_oauth_auth: TestClient) -> None:
    """
    must redirect to OAuth service provider in case if empty code is supplied
    """
    oauth = client_with_oauth_auth.app["validator"]
    oauth.get_oauth_url.return_value = "http://localhost"
    request_schema = pytest.helpers.schema_request(LoginView.get, location="querystring")

    payload = {"code": ""}
    assert not request_schema.validate(payload)
    response = await client_with_oauth_auth.get("/api/v1/login", params=payload, allow_redirects=False)
    assert response.ok
    oauth.get_oauth_url.assert_called_once_with()


async def test_get(client_with_oauth_auth: TestClient, mocker: MockerFixture) -> None:
    """
    must log in user correctly from OAuth
    """
    oauth = client_with_oauth_auth.app["validator"]
    oauth.get_oauth_username.return_value = "user"
    oauth.known_username.return_value = True
    oauth.enabled = False  # lol
    oauth.max_age = 60
    remember_mock = mocker.patch("aiohttp_security.remember")
    request_schema = pytest.helpers.schema_request(LoginView.get, location="querystring")

    payload = {"code": "code"}
    assert not request_schema.validate(payload)
    response = await client_with_oauth_auth.get("/api/v1/login", params=payload)

    assert response.ok
    oauth.get_oauth_username.assert_called_once_with("code")
    oauth.known_username.assert_called_once_with("user")
    remember_mock.assert_called_once_with(
        pytest.helpers.anyvar(int), pytest.helpers.anyvar(int), pytest.helpers.anyvar(int))


async def test_get_unauthorized(client_with_oauth_auth: TestClient, mocker: MockerFixture) -> None:
    """
    must return unauthorized from OAuth
    """
    oauth = client_with_oauth_auth.app["validator"]
    oauth.known_username.return_value = False
    oauth.max_age = 60
    remember_mock = mocker.patch("aiohttp_security.remember")
    response_schema = pytest.helpers.schema_response(LoginView.post, code=401)

    response = await client_with_oauth_auth.get(
        "/api/v1/login", params={"code": "code"}, headers={"accept": "application/json"})

    assert response.status == 401
    assert not response_schema.validate(await response.json())
    remember_mock.assert_not_called()


async def test_post(client_with_auth: TestClient, user: User, mocker: MockerFixture) -> None:
    """
    must log in user correctly
    """
    payload = {"username": user.username, "password": user.password}
    remember_mock = mocker.patch("aiohttp_security.remember")
    request_schema = pytest.helpers.schema_request(LoginView.post)

    assert not request_schema.validate(payload)

    response = await client_with_auth.post("/api/v1/login", json=payload)
    assert response.ok

    response = await client_with_auth.post("/api/v1/login", data=payload)
    assert response.ok

    remember_mock.assert_called()


async def test_post_skip(client: TestClient, user: User) -> None:
    """
    must process if no auth configured
    """
    request_schema = pytest.helpers.schema_request(LoginView.post)

    payload = {"username": user.username, "password": user.password}
    assert not request_schema.validate(payload)
    response = await client.post("/api/v1/login", json=payload)
    assert response.ok


async def test_post_unauthorized(client_with_auth: TestClient, user: User, mocker: MockerFixture) -> None:
    """
    must return unauthorized on invalid auth
    """
    response_schema = pytest.helpers.schema_response(LoginView.post, code=401)

    payload = {"username": user.username, "password": ""}
    remember_mock = mocker.patch("aiohttp_security.remember")

    response = await client_with_auth.post("/api/v1/login", json=payload, headers={"accept": "application/json"})
    assert response.status == 401
    assert not response_schema.validate(await response.json())
    remember_mock.assert_not_called()
