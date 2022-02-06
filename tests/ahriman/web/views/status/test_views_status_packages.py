import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.user_access import UserAccess
from ahriman.web.views.status.packages import PackagesView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET", "HEAD"):
        request = pytest.helpers.request("", "", method)
        assert await PackagesView.get_permission(request) == UserAccess.Read
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await PackagesView.get_permission(request) == UserAccess.Write


async def test_get(client: TestClient, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must return status for all packages
    """
    await client.post(f"/status-api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    await client.post(f"/status-api/v1/packages/{package_python_schedule.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_python_schedule.view()})

    response = await client.get("/status-api/v1/packages")
    assert response.ok

    packages = [Package.from_json(item["package"]) for item in await response.json()]
    assert packages
    assert {package.base for package in packages} == {package_ahriman.base, package_python_schedule.base}


async def test_post(client: TestClient, mocker: MockerFixture) -> None:
    """
    must be able to reload packages
    """
    load_mock = mocker.patch("ahriman.core.status.watcher.Watcher.load")
    response = await client.post("/status-api/v1/packages")
    assert response.status == 204
    load_mock.assert_called_once()
