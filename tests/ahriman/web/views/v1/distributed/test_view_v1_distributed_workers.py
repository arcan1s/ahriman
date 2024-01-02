import pytest

from aiohttp.test_utils import TestClient

from ahriman.models.user_access import UserAccess
from ahriman.models.worker import Worker
from ahriman.web.views.v1.distributed.workers import WorkersView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("DELETE", "GET", "POST"):
        request = pytest.helpers.request("", "", method)
        assert await WorkersView.get_permission(request) == UserAccess.Full


def test_routes() -> None:
    """
    must return correct routes
    """
    assert WorkersView.ROUTES == ["/api/v1/distributed"]


async def test_delete(client: TestClient) -> None:
    """
    must delete all workers
    """
    await client.post("/api/v1/distributed", json={"address": "address1", "identifier": "1"})
    await client.post("/api/v1/distributed", json={"address": "address2", "identifier": "2"})

    response = await client.delete("/api/v1/distributed")
    assert response.status == 204

    response = await client.get("/api/v1/distributed")
    json = await response.json()
    assert not json


async def test_get(client: TestClient) -> None:
    """
    must return all workers
    """
    await client.post("/api/v1/distributed", json={"address": "address1", "identifier": "1"})
    await client.post("/api/v1/distributed", json={"address": "address2", "identifier": "2"})
    response_schema = pytest.helpers.schema_response(WorkersView.get)

    response = await client.get("/api/v1/distributed")
    assert response.ok
    json = await response.json()
    assert not response_schema.validate(json, many=True)

    workers = [Worker(item["address"], identifier=item["identifier"]) for item in json]
    assert workers == [Worker("address1", identifier="1"), Worker("address2", identifier="2")]


async def test_post(client: TestClient) -> None:
    """
    must update worker
    """
    worker = Worker("address1", identifier="1")
    request_schema = pytest.helpers.schema_request(WorkersView.post)

    payload = worker.view()
    assert not request_schema.validate(payload)

    response = await client.post("/api/v1/distributed", json=payload)
    assert response.status == 204


async def test_post_exception(client: TestClient) -> None:
    """
    must raise exception on invalid payload
    """
    response_schema = pytest.helpers.schema_response(WorkersView.post, code=400)

    response = await client.post("/api/v1/distributed", json={})
    assert response.status == 400
    assert not response_schema.validate(await response.json())
