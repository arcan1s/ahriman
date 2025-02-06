import pytest

from aiohttp.test_utils import TestClient

from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.service.logs import LogsView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("DELETE",):
        request = pytest.helpers.request("", "", method)
        assert await LogsView.get_permission(request) == UserAccess.Full


def test_routes() -> None:
    """
    must return correct routes
    """
    assert LogsView.ROUTES == ["/api/v1/service/logs"]


async def test_delete(client: TestClient, package_ahriman: Package) -> None:
    """
    must delete all logs
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    await client.post(f"/api/v1/packages/{package_ahriman.base}/logs",
                      json={"created": 42.0, "message": "message 1", "version": "42"})
    await client.post(f"/api/v1/packages/{package_ahriman.base}/logs",
                      json={"created": 43.0, "message": "message 2", "version": "43"})

    response = await client.delete("/api/v1/service/logs")
    assert response.status == 204

    response = await client.get(f"/api/v2/packages/{package_ahriman.base}/logs")
    json = await response.json()
    assert not json


async def test_delete_partially(client: TestClient, package_ahriman: Package) -> None:
    """
    must delete logs based on count input
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    await client.post(f"/api/v1/packages/{package_ahriman.base}/logs",
                      json={"created": 42.0, "message": "message 1", "version": "42"})
    await client.post(f"/api/v1/packages/{package_ahriman.base}/logs",
                      json={"created": 43.0, "message": "message 2", "version": "43"})
    request_schema = pytest.helpers.schema_request(LogsView.delete, location="querystring")

    payload = {"keep_last_records": 1}
    assert not request_schema.validate(payload)

    response = await client.delete("/api/v1/service/logs", params=payload)
    assert response.status == 204

    response = await client.get(f"/api/v2/packages/{package_ahriman.base}/logs")
    json = await response.json()
    assert json


async def test_delete_exception(client: TestClient, package_ahriman: Package) -> None:
    """
    must raise exception on invalid payload
    """
    response_schema = pytest.helpers.schema_response(LogsView.delete, code=400)

    response = await client.delete("/api/v1/service/logs", params={"keep_last_records": "string"})
    assert response.status == 400
    assert not response_schema.validate(await response.json())
