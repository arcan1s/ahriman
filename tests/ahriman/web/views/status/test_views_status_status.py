import pytest

from aiohttp.test_utils import TestClient

import ahriman.version as version

from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.user_access import UserAccess
from ahriman.web.views.status.status import StatusView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET", "HEAD"):
        request = pytest.helpers.request("", "", method)
        assert await StatusView.get_permission(request) == UserAccess.Read


async def test_get(client: TestClient, package_ahriman: Package) -> None:
    """
    must generate web service status correctly
    """
    await client.post(f"/status-api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})

    response = await client.get("/status-api/v1/status")
    assert response.ok

    json = await response.json()
    assert json["version"] == version.__version__
    assert json["packages"]
    assert json["packages"]["total"] == 1
