import pytest

from aiohttp.test_utils import TestClient

from ahriman.models.user_access import UserAccess
from ahriman.models.worker import Worker
from ahriman.web.views.v1.distributed.worker import WorkerView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("DELETE", "GET"):
        request = pytest.helpers.request("", "", method)
        assert await WorkerView.get_permission(request) == UserAccess.Full


def test_routes() -> None:
    """
    must return correct routes
    """
    assert WorkerView.ROUTES == ["/api/v1/distributed/{identifier}"]


async def test_delete(client: TestClient) -> None:
    """
    must delete single worker
    """
    await client.post("/api/v1/distributed", json={"address": "address1", "identifier": "1"})
    await client.post("/api/v1/distributed", json={"address": "address2", "identifier": "2"})

    response = await client.delete("/api/v1/distributed/1")
    assert response.status == 204

    response = await client.get("/api/v1/distributed/1")
    assert response.status == 404

    response = await client.get("/api/v1/distributed/2")
    assert response.ok


async def test_get(client: TestClient) -> None:
    """
    must return specific worker
    """
    worker = Worker("address1", identifier="1")

    await client.post("/api/v1/distributed", json=worker.view())
    await client.post("/api/v1/distributed", json={"address": "address2", "identifier": "2"})
    response_schema = pytest.helpers.schema_response(WorkerView.get)

    response = await client.get(f"/api/v1/distributed/{worker.identifier}")
    assert response.ok
    json = await response.json()
    assert not response_schema.validate(json, many=True)

    workers = [Worker(item["address"], identifier=item["identifier"]) for item in json]
    assert workers == [worker]


async def test_get_not_found(client: TestClient) -> None:
    """
    must return Not Found for unknown package
    """
    response_schema = pytest.helpers.schema_response(WorkerView.get, code=404)

    response = await client.get("/api/v1/distributed/1")
    assert response.status == 404
    assert not response_schema.validate(await response.json())
