import pytest

from aiohttp.test_utils import TestClient

from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.status.patches import PatchesView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await PatchesView.get_permission(request) == UserAccess.Reporter
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await PatchesView.get_permission(request) == UserAccess.Full


def test_routes() -> None:
    """
    must return correct routes
    """
    assert PatchesView.ROUTES == ["/api/v1/packages/{package}/patches"]


async def test_get(client: TestClient, package_ahriman: Package) -> None:
    """
    must get patch for package
    """
    patch = PkgbuildPatch("k", "v")
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    await client.post(f"/api/v1/packages/{package_ahriman.base}/patches", json=patch.view())
    response_schema = pytest.helpers.schema_response(PatchesView.get)

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}/patches")
    assert response.status == 200

    patches = await response.json()
    assert not response_schema.validate(patches)
    assert patches == [patch.view()]


async def test_post(client: TestClient, package_ahriman: Package) -> None:
    """
    must create patch
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    request_schema = pytest.helpers.schema_request(PatchesView.post)

    payload = {"key": "k", "value": "v"}
    assert not request_schema.validate(payload)
    response = await client.post(f"/api/v1/packages/{package_ahriman.base}/patches", json=payload)
    assert response.status == 204

    response = await client.get(f"/api/v1/packages/{package_ahriman.base}/patches")
    patches = await response.json()
    assert patches == [payload]


async def test_post_exception(client: TestClient, package_ahriman: Package) -> None:
    """
    must raise exception on invalid payload
    """
    response_schema = pytest.helpers.schema_response(PatchesView.post, code=400)

    response = await client.post(f"/api/v1/packages/{package_ahriman.base}/patches", json={})
    assert response.status == 400
    assert not response_schema.validate(await response.json())
