import pytest

from aiohttp.test_utils import TestClient

from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.user_access import UserAccess
from ahriman.web.views.status.logs import LogsView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await LogsView.get_permission(request) == UserAccess.Reporter
    for method in ("DELETE", "POST"):
        request = pytest.helpers.request("", "", method)
        assert await LogsView.get_permission(request) == UserAccess.Full


async def test_delete(client: TestClient, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must delete logs for package
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    await client.post(f"/api/v1/packages/{package_python_schedule.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_python_schedule.view()})

    await client.post(f"/api/v1/packages/{package_ahriman.base}/logs",
                      json={"created": 42.0, "message": "message", "process_id": 42})
    await client.post(f"/api/v1/packages/{package_python_schedule.base}/logs",
                      json={"created": 42.0, "message": "message", "process_id": 42})

    response = await client.delete(f"/api/v1/packages/{package_ahriman.base}/logs")
    assert response.status == 204

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}/logs")
    logs = await response.json()
    assert not logs["logs"]

    response = await client.get(f"/api/v1/packages/{package_python_schedule.base}/logs")
    logs = await response.json()
    assert logs["logs"]


async def test_get(client: TestClient, package_ahriman: Package) -> None:
    """
    must get logs for package
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    await client.post(f"/api/v1/packages/{package_ahriman.base}/logs",
                      json={"created": 42.0, "message": "message", "process_id": 42})
    response_schema = pytest.helpers.schema_response(LogsView.get)

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}/logs")
    assert response.status == 200

    logs = await response.json()
    assert not response_schema.validate(logs)
    assert logs["logs"] == "[1970-01-01 00:00:42] message"


async def test_get_not_found(client: TestClient, package_ahriman: Package) -> None:
    """
    must return not found for missing package
    """
    response_schema = pytest.helpers.schema_response(LogsView.get, code=404)

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}/logs")
    assert response.status == 404
    assert not response_schema.validate(await response.json())


async def test_post(client: TestClient, package_ahriman: Package) -> None:
    """
    must create logs record
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    request_schema = pytest.helpers.schema_request(LogsView.post)

    payload = {"created": 42.0, "message": "message", "process_id": 42}
    assert not request_schema.validate(payload)
    response = await client.post(f"/api/v1/packages/{package_ahriman.base}/logs", json=payload)
    assert response.status == 204

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}/logs")
    logs = await response.json()
    assert logs["logs"] == "[1970-01-01 00:00:42] message"


async def test_post_exception(client: TestClient, package_ahriman: Package) -> None:
    """
    must raise exception on invalid payload
    """
    response_schema = pytest.helpers.schema_response(LogsView.post, code=400)

    response = await client.post(f"/api/v1/packages/{package_ahriman.base}/logs", json={})
    assert response.status == 400
    assert not response_schema.validate(await response.json())
