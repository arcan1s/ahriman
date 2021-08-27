from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.core.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.models.user import User


async def test_post(client: TestClient, configuration: Configuration, user: User, mocker: MockerFixture) -> None:
    """
    must login user correctly
    """
    client.app["validator"] = Auth(configuration)
    payload = {"username": user.username, "password": user.password}
    remember_patch = mocker.patch("aiohttp_security.remember")
    mocker.patch("ahriman.core.auth.Auth.check_credentials", return_value=True)

    post_response = await client.post("/login", json=payload)
    assert post_response.status == 200

    post_response = await client.post("/login", data=payload)
    assert post_response.status == 200

    remember_patch.assert_called()


async def test_post_skip(client: TestClient, user: User, mocker: MockerFixture) -> None:
    """
    must process if no auth configured
    """
    payload = {"username": user.username, "password": user.password}
    post_response = await client.post("/login", json=payload)
    remember_patch = mocker.patch("aiohttp_security.remember")
    assert post_response.status == 200
    remember_patch.assert_not_called()


async def test_post_unauthorized(client: TestClient, configuration: Configuration, user: User,
                                 mocker: MockerFixture) -> None:
    """
    must return unauthorized on invalid auth
    """
    client.app["validator"] = Auth(configuration)
    payload = {"username": user.username, "password": user.password}
    mocker.patch("ahriman.core.auth.Auth.check_credentials", return_value=False)

    post_response = await client.post("/login", json=payload)
    assert post_response.status == 401
