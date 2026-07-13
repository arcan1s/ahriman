import pytest

from aiohttp.test_utils import TestClient

from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.packages.patch import PatchView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await PatchView.get_permission(request) == UserAccess.Reporter
    for method in ("DELETE",):
        request = pytest.helpers.request("", "", method)
        assert await PatchView.get_permission(request) == UserAccess.Full


def test_routes() -> None:
    """
    must return correct routes
    """
    assert PatchView.ROUTES == ["/api/v1/packages/{package}/patches/{patch}"]


async def test_delete(client: TestClient, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must delete patch for package
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    await client.post(f"/api/v1/packages/{package_python_schedule.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_python_schedule.view()})

    patch_key = "k"
    await client.post(f"/api/v1/packages/{package_ahriman.base}/patches", json={"key": patch_key, "value": "v"})
    await client.post(f"/api/v1/packages/{package_python_schedule.base}/patches",
                      json={"key": patch_key, "value": "v2"})

    response = await client.delete(f"/api/v1/packages/{package_ahriman.base}/patches/{patch_key}")
    assert response.status == 204

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}/patches")
    assert not await response.json()

    response = await client.get(f"/api/v1/packages/{package_python_schedule.base}/patches")
    assert await response.json()


async def test_get(client: TestClient, package_ahriman: Package) -> None:
    """
    must get patch for package
    """
    patch = PkgbuildPatch("k", "v")
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    await client.post(f"/api/v1/packages/{package_ahriman.base}/patches", json=patch.view())
    response_schema = pytest.helpers.schema_response(PatchView.get)

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}/patches/{patch.key}")
    assert response.status == 200

    patches = await response.json()
    assert not response_schema.validate(patches)
    assert patches == patch.view()


async def test_get_patch_not_found(client: TestClient, package_ahriman: Package) -> None:
    """
    must return not found for missing patch
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    response_schema = pytest.helpers.schema_response(PatchView.get, code=404)

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}/patches/random")
    assert response.status == 404
    assert not response_schema.validate(await response.json())
