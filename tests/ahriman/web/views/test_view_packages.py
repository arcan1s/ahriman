from pytest_aiohttp import TestClient
from pytest_mock import MockerFixture

from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package


async def test_get(client: TestClient, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must return status for all packages
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    await client.post(f"/api/v1/packages/{package_python_schedule.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_python_schedule.view()})

    response = await client.get("/api/v1/packages")
    assert response.status == 200

    packages = [Package.from_json(item["package"]) for item in await response.json()]
    assert packages
    assert {package.base for package in packages} == {package_ahriman.base, package_python_schedule.base}


async def test_post(client: TestClient, mocker: MockerFixture) -> None:
    """
    must be able to reload packages
    """
    load_mock = mocker.patch("ahriman.core.status.watcher.Watcher.load")
    response = await client.post("/api/v1/packages")
    assert response.status == 204
    load_mock.assert_called_once()
