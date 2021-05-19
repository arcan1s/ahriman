from pytest_aiohttp import TestClient

import ahriman.version as version

from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package


async def test_get(client: TestClient, package_ahriman: Package) -> None:
    """
    must generate web service status correctly
    """
    await client.post(f"/api/v1/packages/{package_ahriman.base}",
                      json={"status": BuildStatusEnum.Success.value, "package": package_ahriman.view()})

    response = await client.get("/api/v1/status")
    assert response.status == 200

    json = await response.json()
    assert json["version"] == version.__version__
    assert json["packages"]
    assert json["packages"]["total"] == 1
