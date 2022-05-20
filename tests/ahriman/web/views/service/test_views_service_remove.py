import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.user_access import UserAccess
from ahriman.web.views.service.remove import RemoveView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await RemoveView.get_permission(request) == UserAccess.Full


async def test_post(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call post request correctly
    """
    remove_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_remove")
    response = await client.post("/service-api/v1/remove", json={"packages": ["ahriman"]})

    assert response.ok
    remove_mock.assert_called_once_with(["ahriman"])


async def test_post_exception(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise exception on missing packages payload
    """
    remove_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_remove")
    response = await client.post("/service-api/v1/remove")

    assert response.status == 400
    remove_mock.assert_not_called()
