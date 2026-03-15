import pytest

from aiohttp.test_utils import TestClient

from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.packages.hold import HoldView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await HoldView.get_permission(request) == UserAccess.Full


def test_routes() -> None:
    """
    must return correct routes
    """
    assert HoldView.ROUTES == ["/api/v1/packages/{package}/hold"]


async def test_post(client: TestClient, package_ahriman: Package) -> None:
    """
    must update package hold status
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})
    request_schema = pytest.helpers.schema_request(HoldView.post)

    payload = {"is_held": True}
    assert not request_schema.validate(payload)
    response = await client.post(f"/api/v1/packages/{package_ahriman.base}/hold", json=payload)
    assert response.status == 204


async def test_post_exception(client: TestClient, package_ahriman: Package) -> None:
    """
    must raise exception on invalid payload
    """
    response_schema = pytest.helpers.schema_response(HoldView.post, code=400)

    response = await client.post(f"/api/v1/packages/{package_ahriman.base}/hold", json=[])
    assert response.status == 400
    assert not response_schema.validate(await response.json())
