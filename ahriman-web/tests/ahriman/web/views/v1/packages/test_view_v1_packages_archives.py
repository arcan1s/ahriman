import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.packages.archives import Archives


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await Archives.get_permission(request) == UserAccess.Reporter


def test_routes() -> None:
    """
    must return correct routes
    """
    assert Archives.ROUTES == ["/api/v1/packages/{package}/archives"]


async def test_get(client: TestClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must get archives for package
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    mocker.patch("ahriman.core.status.watcher.Watcher.package_archives", return_value=[package_ahriman])
    response_schema = pytest.helpers.schema_response(Archives.get)

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}/archives")
    assert response.status == 200

    archives = await response.json()
    assert not response_schema.validate(archives)


async def test_get_not_found(client: TestClient, package_ahriman: Package) -> None:
    """
    must return not found for missing package
    """
    response_schema = pytest.helpers.schema_response(Archives.get, code=404)

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}/archives")
    assert response.status == 404
    assert not response_schema.validate(await response.json())
