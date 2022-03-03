import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.user_access import UserAccess
from ahriman.web.views.service.reload_auth import ReloadAuthView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await ReloadAuthView.get_permission(request) == UserAccess.Write


async def test_post(client_with_auth: TestClient, mocker: MockerFixture) -> None:
    """
    must call post request correctly
    """
    mocker.patch("aiohttp_security.check_permission", return_value=True)
    reload_mock = mocker.patch("ahriman.core.configuration.Configuration.reload")
    load_mock = mocker.patch("ahriman.core.auth.auth.Auth.load")
    response = await client_with_auth.post("/service-api/v1/reload-auth")

    assert response.ok
    reload_mock.assert_called_once_with()
    load_mock.assert_called_once_with(client_with_auth.app["configuration"])


async def test_post_no_auth(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call return 500 if no authorization module loaded
    """
    reload_mock = mocker.patch("ahriman.core.configuration.Configuration.reload")
    response = await client.post("/service-api/v1/reload-auth")

    assert response.status == 500
    reload_mock.assert_called_once_with()
