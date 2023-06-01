from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture
from unittest.mock import AsyncMock


async def test_post_update(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call post request correctly for alias
    """
    update_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_update")
    user_mock = AsyncMock()
    user_mock.return_value = "username"
    mocker.patch("ahriman.web.views.base.BaseView.username", side_effect=user_mock)

    response = await client.post("/api/v1/service/update")
    assert response.ok
    update_mock.assert_called_once_with("username")
