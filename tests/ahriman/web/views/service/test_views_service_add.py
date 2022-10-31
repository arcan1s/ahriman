import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.user_access import UserAccess
from ahriman.web.views.service.add import AddView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await AddView.get_permission(request) == UserAccess.Full


async def test_post(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call post request correctly
    """
    add_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_add")
    response = await client.post("/api/v1/service/add", json={"packages": ["ahriman"]})

    assert response.ok
    add_mock.assert_called_once_with(["ahriman"], now=True)


async def test_post_update(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call post request correctly for alias
    """
    add_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_add")
    response = await client.post("/api/v1/service/update", json={"packages": ["ahriman"]})

    assert response.ok
    add_mock.assert_called_once_with(["ahriman"], now=True)
