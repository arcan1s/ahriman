from aiohttp.test_utils import TestClient
from aiohttp.web import HTTPUnauthorized
from pytest_mock import MockerFixture


async def test_post(client_with_auth: TestClient, mocker: MockerFixture) -> None:
    """
    must logout user correctly
    """
    mocker.patch("aiohttp_security.check_authorized")
    forget_mock = mocker.patch("aiohttp_security.forget")

    post_response = await client_with_auth.post("/user-api/v1/logout")
    assert post_response.status == 200
    forget_mock.assert_called_once()


async def test_post_unauthorized(client_with_auth: TestClient, mocker: MockerFixture) -> None:
    """
    must raise exception if unauthorized
    """
    mocker.patch("aiohttp_security.check_authorized", side_effect=HTTPUnauthorized())
    forget_mock = mocker.patch("aiohttp_security.forget")

    post_response = await client_with_auth.post("/user-api/v1/logout")
    assert post_response.status == 401
    forget_mock.assert_not_called()


async def test_post_disabled(client: TestClient) -> None:
    """
    must raise exception if auth is disabled
    """
    post_response = await client.post("/user-api/v1/logout")
    assert post_response.status == 200
