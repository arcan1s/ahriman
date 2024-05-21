import pytest

from aiohttp.test_utils import TestClient

from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.dependencies import Dependencies
from ahriman.models.package import Package
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.packages.dependencies import DependenciesView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await DependenciesView.get_permission(request) == UserAccess.Reporter
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await DependenciesView.get_permission(request) == UserAccess.Full


def test_routes() -> None:
    """
    must return correct routes
    """
    assert DependenciesView.ROUTES == ["/api/v1/packages/{package}/dependencies"]


async def test_get(client: TestClient, package_ahriman: Package) -> None:
    """
    must get dependencies for package
    """
    dependency = Dependencies({"path": ["package"]})
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    await client.post(f"/api/v1/packages/{package_ahriman.base}/dependencies", json=dependency.view())
    response_schema = pytest.helpers.schema_response(DependenciesView.get)

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}/dependencies")
    assert response.status == 200

    dependencies = await response.json()
    assert not response_schema.validate(dependencies)
    assert dependencies == dependency.view()


async def test_get_not_found(client: TestClient, package_ahriman: Package) -> None:
    """
    must return not found for missing package
    """
    response_schema = pytest.helpers.schema_response(DependenciesView.get, code=404)

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}/dependencies")
    assert response.status == 404
    assert not response_schema.validate(await response.json())


async def test_post(client: TestClient, package_ahriman: Package) -> None:
    """
    must create dependencies
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    request_schema = pytest.helpers.schema_request(DependenciesView.post)

    payload = {"paths": {"path": ["package"]}}
    assert not request_schema.validate(payload)
    response = await client.post(f"/api/v1/packages/{package_ahriman.base}/dependencies", json=payload)
    assert response.status == 204

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}/dependencies")
    dependencies = await response.json()
    assert dependencies == payload


async def test_post_exception(client: TestClient, package_ahriman: Package) -> None:
    """
    must raise exception on invalid payload
    """
    response_schema = pytest.helpers.schema_response(DependenciesView.post, code=400)

    response = await client.post(f"/api/v1/packages/{package_ahriman.base}/dependencies", json=[])
    assert response.status == 400
    assert not response_schema.validate(await response.json())


async def test_post_not_found(client: TestClient, package_ahriman: Package) -> None:
    """
    must raise exception on unknown package
    """
    response_schema = pytest.helpers.schema_response(DependenciesView.post, code=404)

    response = await client.post(f"/api/v1/packages/{package_ahriman.base}/dependencies", json={})
    assert response.status == 404
    assert not response_schema.validate(await response.json())
