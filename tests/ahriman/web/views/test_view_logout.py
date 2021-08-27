from aiohttp.test_utils import TestClient
from aiohttp.web import HTTPUnauthorized
from pytest_mock import MockerFixture


async def test_post(client: TestClient, mocker: MockerFixture) -> None:
    """
    must logout user correctly
    """
    mocker.patch("aiohttp_security.check_authorized")
    forget_patch = mocker.patch("aiohttp_security.forget")

    post_response = await client.post("/logout")
    assert post_response.status == 200
    forget_patch.assert_called_once()


async def test_post_unauthorized(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise exception if unauthorized
    """
    mocker.patch("aiohttp_security.check_authorized", side_effect=HTTPUnauthorized())
    forget_patch = mocker.patch("aiohttp_security.forget")

    post_response = await client.post("/logout")
    assert post_response.status == 401
    forget_patch.assert_not_called()


async def test_post_disabled(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise exception if auth is disabled
    """
    forget_patch = mocker.patch("aiohttp_security.forget")

    post_response = await client.post("/logout")
    assert post_response.status == 401
    forget_patch.assert_not_called()
