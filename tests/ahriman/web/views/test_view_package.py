from pytest_aiohttp import TestClient

from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.package import Package


async def test_get(client: TestClient, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must return status for specific package
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    await client.post(f"/api/v1/packages/{package_python_schedule.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_python_schedule.view()})

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}")
    assert response.status == 200

    packages = [Package.from_json(item["package"]) for item in await response.json()]
    assert packages
    assert {package.base for package in packages} == {package_ahriman.base}


async def test_get_not_found(client: TestClient, package_ahriman: Package) -> None:
    """
    must return Not Found for unknown package
    """
    response = await client.get(f"/api/v1/packages/{package_ahriman.base}")
    assert response.status == 404


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
    assert response.status == 200


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
    assert response.status == 200


async def test_post(client: TestClient, package_ahriman: Package) -> None:
    """
    must update package status
    """
    post_response = await client.post(
        f"/api/v1/packages/{package_ahriman.base}",
        json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    assert post_response.status == 204

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}")
    assert response.status == 200


async def test_post_exception(client: TestClient, package_ahriman: Package) -> None:
    """
    must raise exception on invalid payload
    """
    post_response = await client.post(f"/api/v1/packages/{package_ahriman.base}", json={})
    assert post_response.status == 400


async def test_post_light(client: TestClient, package_ahriman: Package) -> None:
    """
    must update package status only
    """
    post_response = await client.post(
        f"/api/v1/packages/{package_ahriman.base}",
        json={"status": BuildStatusEnum.Unknown.value, "package": package_ahriman.view()})
    assert post_response.status == 204

    post_response = await client.post(
        f"/api/v1/packages/{package_ahriman.base}", json={"status": BuildStatusEnum.Success.value})
    assert post_response.status == 204

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}")
    assert response.status == 200
    statuses = {
        Package.from_json(item["package"]).base: BuildStatus.from_json(item["status"])
        for item in await response.json()
    }
    assert statuses[package_ahriman.base].status == BuildStatusEnum.Success


async def test_post_not_found(client: TestClient, package_ahriman: Package) -> None:
    """
    must raise exception on status update for unknown package
    """
    post_response = await client.post(
        f"/api/v1/packages/{package_ahriman.base}", json={"status": BuildStatusEnum.Success.value})
    assert post_response.status == 400
