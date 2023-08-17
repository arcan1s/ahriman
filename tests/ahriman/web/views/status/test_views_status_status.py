import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman import __version__
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.internal_status import InternalStatus
from ahriman.models.package import Package
from ahriman.models.user_access import UserAccess
from ahriman.web.views.status.status import StatusView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await StatusView.get_permission(request) == UserAccess.Read
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await StatusView.get_permission(request) == UserAccess.Full


async def test_get(client: TestClient, package_ahriman: Package) -> None:
    """
    must generate web service status correctly
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    response_schema = pytest.helpers.schema_response(StatusView.get)

    response = await client.get("/api/v1/status")
    assert response.ok
    json = await response.json()
    assert not response_schema.validate(json)

    assert json["version"] == __version__
    assert json["packages"]
    assert json["packages"]["total"] == 1


async def test_post(client: TestClient) -> None:
    """
    must update service status correctly
    """
    request_schema = pytest.helpers.schema_request(StatusView.post)

    payload = {"status": BuildStatusEnum.Success.value}
    assert not request_schema.validate(payload)
    post_response = await client.post("/api/v1/status", json=payload)
    assert post_response.status == 204

    response = await client.get("/api/v1/status")
    status = InternalStatus.from_json(await response.json())

    assert response.ok
    assert status.status.status == BuildStatusEnum.Success


async def test_post_exception(client: TestClient) -> None:
    """
    must raise exception on invalid payload
    """
    response_schema = pytest.helpers.schema_response(StatusView.post, code=400)

    response = await client.post("/api/v1/status", json={})
    assert response.status == 400
    assert not response_schema.validate(await response.json())


async def test_post_exception_inside(client: TestClient, mocker: MockerFixture) -> None:
    """
    exception handler must handle 500 errors
    """
    payload = {"status": BuildStatusEnum.Success.value}
    mocker.patch("ahriman.core.status.watcher.Watcher.status_update", side_effect=Exception())
    response_schema = pytest.helpers.schema_response(StatusView.post, code=500)

    response = await client.post("/api/v1/status", json=payload)
    assert response.status == 500
    assert not response_schema.validate(await response.json())
