import pytest

from aiohttp.test_utils import TestClient

from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v2.packages.logs import LogsView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await LogsView.get_permission(request) == UserAccess.Reporter


def test_routes() -> None:
    """
    must return correct routes
    """
    assert LogsView.ROUTES == ["/api/v2/packages/{package}/logs"]


async def test_get(client: TestClient, package_ahriman: Package) -> None:
    """
    must get logs for package
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    await client.post(f"/api/v1/packages/{package_ahriman.base}/logs",
                      json={"created": 42.0, "message": "message 1", "version": "42"})
    await client.post(f"/api/v1/packages/{package_ahriman.base}/logs",
                      json={"created": 43.0, "message": "message 2", "version": "42"})
    request_schema = pytest.helpers.schema_request(LogsView.get, location="querystring")
    response_schema = pytest.helpers.schema_response(LogsView.get)

    payload = {}
    assert not request_schema.validate(payload)
    response = await client.get(f"/api/v2/packages/{package_ahriman.base}/logs", params=payload)
    assert response.status == 200

    logs = await response.json()
    assert not response_schema.validate(logs)
    assert logs == [
        {
            "created": 42.0,
            "message": "message 1",
        },
        {
            "created": 43.0,
            "message": "message 2",
        },
    ]


async def test_get_with_pagination(client: TestClient, package_ahriman: Package) -> None:
    """
    must get logs with pagination
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    await client.post(f"/api/v1/packages/{package_ahriman.base}/logs",
                      json={"created": 42.0, "message": "message 1", "version": "42"})
    await client.post(f"/api/v1/packages/{package_ahriman.base}/logs",
                      json={"created": 43.0, "message": "message 2", "version": "42"})
    request_schema = pytest.helpers.schema_request(LogsView.get, location="querystring")
    response_schema = pytest.helpers.schema_response(LogsView.get)

    payload = {"limit": 1, "offset": 1}
    assert not request_schema.validate(payload)
    response = await client.get(f"/api/v2/packages/{package_ahriman.base}/logs", params=payload)
    assert response.status == 200

    logs = await response.json()
    assert not response_schema.validate(logs)
    assert logs == [{"created": 43.0, "message": "message 2"}]


async def test_get_bad_request(client: TestClient, package_ahriman: Package) -> None:
    """
    must return bad request for invalid query parameters
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    await client.post(f"/api/v1/packages/{package_ahriman.base}/logs",
                      json={"created": 42.0, "message": "message", "version": "42"})
    response_schema = pytest.helpers.schema_response(LogsView.get, code=400)

    response = await client.get(f"/api/v2/packages/{package_ahriman.base}/logs", params={"limit": "limit"})
    assert response.status == 400
    assert not response_schema.validate(await response.json())

    response = await client.get(f"/api/v2/packages/{package_ahriman.base}/logs", params={"offset": "offset"})
    assert response.status == 400
    assert not response_schema.validate(await response.json())


async def test_get_not_found(client: TestClient, package_ahriman: Package) -> None:
    """
    must return not found for missing package
    """
    response_schema = pytest.helpers.schema_response(LogsView.get, code=404)

    response = await client.get(f"/api/v2/packages/{package_ahriman.base}/logs")
    assert response.status == 404
    assert not response_schema.validate(await response.json())
