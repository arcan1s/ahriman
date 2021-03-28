from aiohttp.test_utils import TestClient

from ahriman.models.build_status import BuildStatus, BuildStatusEnum


async def test_get(client: TestClient) -> None:
    """
    must return valid service status
    """
    response = await client.get("/api/v1/ahriman")
    status = BuildStatus.from_json(await response.json())

    assert response.status == 200
    assert status.status == BuildStatusEnum.Unknown


async def test_post(client: TestClient) -> None:
    """
    must update service status correctly
    """
    payload = {"status": BuildStatusEnum.Success.value}
    post_response = await client.post("/api/v1/ahriman", json=payload)
    assert post_response.status == 204

    response = await client.get("/api/v1/ahriman")
    status = BuildStatus.from_json(await response.json())

    assert response.status == 200
    assert status.status == BuildStatusEnum.Success


async def test_post_exception(client: TestClient) -> None:
    """
    must raise exception on invalid payload
    """
    post_response = await client.post("/api/v1/ahriman", json={})
    assert post_response.status == 400
