from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.user import User


async def test_post(client_with_auth: TestClient, user: User, mocker: MockerFixture) -> None:
    """
    must login user correctly
    """
    payload = {"username": user.username, "password": user.password}
    remember_mock = mocker.patch("aiohttp_security.remember")

    post_response = await client_with_auth.post("/login", json=payload)
    assert post_response.status == 200

    post_response = await client_with_auth.post("/login", data=payload)
    assert post_response.status == 200

    remember_mock.assert_called()


async def test_post_skip(client: TestClient, user: User) -> None:
    """
    must process if no auth configured
    """
    payload = {"username": user.username, "password": user.password}
    post_response = await client.post("/login", json=payload)
    assert post_response.status == 200


async def test_post_unauthorized(client_with_auth: TestClient, user: User, mocker: MockerFixture) -> None:
    """
    must return unauthorized on invalid auth
    """
    payload = {"username": user.username, "password": ""}
    remember_mock = mocker.patch("aiohttp_security.remember")

    post_response = await client_with_auth.post("/login", json=payload)
    assert post_response.status == 401
    remember_mock.assert_not_called()
