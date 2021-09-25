import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.user_access import UserAccess
from ahriman.web.views.status.ahriman import AhrimanView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET", "HEAD"):
        request = pytest.helpers.request("", "", method)
        assert await AhrimanView.get_permission(request) == UserAccess.Read
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await AhrimanView.get_permission(request) == UserAccess.Write


async def test_get(client: TestClient) -> None:
    """
    must return valid service status
    """
    response = await client.get("/status-api/v1/ahriman")
    status = BuildStatus.from_json(await response.json())

    assert response.ok
    assert status.status == BuildStatusEnum.Unknown


async def test_post(client: TestClient) -> None:
    """
    must update service status correctly
    """
    payload = {"status": BuildStatusEnum.Success.value}
    post_response = await client.post("/status-api/v1/ahriman", json=payload)
    assert post_response.status == 204

    response = await client.get("/status-api/v1/ahriman")
    status = BuildStatus.from_json(await response.json())

    assert response.ok
    assert status.status == BuildStatusEnum.Success


async def test_post_exception(client: TestClient) -> None:
    """
    must raise exception on invalid payload
    """
    post_response = await client.post("/status-api/v1/ahriman", json={})
    assert post_response.status == 400


async def test_post_exception_inside(client: TestClient, mocker: MockerFixture) -> None:
    """
    exception handler must handle 500 errors
    """
    payload = {"status": BuildStatusEnum.Success.value}
    mocker.patch("ahriman.core.status.watcher.Watcher.update_self", side_effect=Exception())

    post_response = await client.post("/status-api/v1/ahriman", json=payload)
    assert post_response.status == 500
