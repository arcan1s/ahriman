import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.user_access import UserAccess
from ahriman.web.views.service.rebuild import RebuildView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await RebuildView.get_permission(request) == UserAccess.Full


async def test_post(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call post request correctly
    """
    rebuild_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_rebuild")

    response = await client.post("/api/v1/service/rebuild", json={"packages": ["python", "ahriman"]})
    assert response.ok
    rebuild_mock.assert_called_once_with("python")


async def test_post_exception(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise exception on missing packages payload
    """
    rebuild_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_rebuild")

    response = await client.post("/api/v1/service/rebuild")
    assert response.status == 400
    rebuild_mock.assert_not_called()
