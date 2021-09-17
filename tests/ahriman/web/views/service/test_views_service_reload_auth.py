from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture


async def test_post(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call post request correctly
    """
    reload_mock = mocker.patch("ahriman.core.configuration.Configuration.reload")
    load_mock = mocker.patch("ahriman.core.auth.auth.Auth.load")
    response = await client.post("/service-api/v1/reload-auth")

    assert response.ok
    reload_mock.assert_called_once()
    load_mock.assert_called_with(client.app["configuration"])
