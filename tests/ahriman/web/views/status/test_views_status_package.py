import pytest

from aiohttp.test_utils import TestClient

from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.user_access import UserAccess
from ahriman.web.schemas.error_schema import ErrorSchema
from ahriman.web.schemas.package_status_schema import PackageStatusSchema, PackageStatusSimplifiedSchema
from ahriman.web.views.status.package import PackageView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await PackageView.get_permission(request) == UserAccess.Read
    for method in ("DELETE", "POST"):
        request = pytest.helpers.request("", "", method)
        assert await PackageView.get_permission(request) == UserAccess.Full


async def test_delete(client: TestClient, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must delete single base
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    await client.post(f"/api/v1/packages/{package_python_schedule.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_python_schedule.view()})

    response = await client.delete(f"/api/v1/packages/{package_ahriman.base}")
    assert response.status == 204

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}")
    assert response.status == 404

    response = await client.get(f"/api/v1/packages/{package_python_schedule.base}")
    assert response.ok


async def test_delete_unknown(client: TestClient, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must suppress errors on unknown package deletion
    """
    await client.post(f"/api/v1/packages/{package_python_schedule.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_python_schedule.view()})

    response = await client.delete(f"/api/v1/packages/{package_ahriman.base}")
    assert response.status == 204

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}")
    assert response.status == 404

    response = await client.get(f"/api/v1/packages/{package_python_schedule.base}")
    assert response.ok


async def test_get(client: TestClient, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must return status for specific package
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    await client.post(f"/api/v1/packages/{package_python_schedule.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_python_schedule.view()})
    response_schema = PackageStatusSchema()

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}")
    assert response.ok
    json = await response.json()
    assert not response_schema.validate(json, many=True)

    packages = [Package.from_json(item["package"]) for item in json]
    assert packages
    assert {package.base for package in packages} == {package_ahriman.base}


async def test_get_not_found(client: TestClient, package_ahriman: Package) -> None:
    """
    must return Not Found for unknown package
    """
    response_schema = ErrorSchema()

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}")
    assert response.status == 404
    assert not response_schema.validate(await response.json())


async def test_post(client: TestClient, package_ahriman: Package) -> None:
    """
    must update package status
    """
    request_schema = PackageStatusSimplifiedSchema()

    payload = {"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()}
    assert not request_schema.validate(payload)
    response = await client.post(f"/api/v1/packages/{package_ahriman.base}", json=payload)
    assert response.status == 204

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}")
    assert response.ok


async def test_post_exception(client: TestClient, package_ahriman: Package) -> None:
    """
    must raise exception on invalid payload
    """
    response_schema = ErrorSchema()

    response = await client.post(f"/api/v1/packages/{package_ahriman.base}", json={})
    assert response.status == 400
    assert not response_schema.validate(await response.json())


async def test_post_light(client: TestClient, package_ahriman: Package) -> None:
    """
    must update package status only
    """
    request_schema = PackageStatusSimplifiedSchema()

    payload = {"status": BuildStatusEnum.Unknown.value, "package": package_ahriman.view()}
    assert not request_schema.validate(payload)
    response = await client.post(f"/api/v1/packages/{package_ahriman.base}", json=payload)
    assert response.status == 204

    payload = {"status": BuildStatusEnum.Success.value}
    assert not request_schema.validate(payload)
    response = await client.post(f"/api/v1/packages/{package_ahriman.base}", json=payload)
    assert response.status == 204

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}")
    assert response.ok
    statuses = {
        Package.from_json(item["package"]).base: BuildStatus.from_json(item["status"])
        for item in await response.json()
    }
    assert statuses[package_ahriman.base].status == BuildStatusEnum.Success


async def test_post_not_found(client: TestClient, package_ahriman: Package) -> None:
    """
    must raise exception on status update for unknown package
    """
    request_schema = PackageStatusSimplifiedSchema()
    response_schema = ErrorSchema()

    payload = {"status": BuildStatusEnum.Success.value}
    assert not request_schema.validate(payload)
    response = await client.post(f"/api/v1/packages/{package_ahriman.base}", json=payload)
    assert response.status == 400
    assert not response_schema.validate(await response.json())
