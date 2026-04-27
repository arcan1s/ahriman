import asyncio
import pytest

from aiohttp.test_utils import TestClient
from asyncio import Queue
from pytest_mock import MockerFixture
from unittest.mock import AsyncMock

from ahriman.core.status.watcher import Watcher
from ahriman.models.event import EventType
from ahriman.models.package import Package
from ahriman.models.user_access import UserAccess
from ahriman.web.keys import WatcherKey
from ahriman.web.views.v1.auditlog.event_bus import EventBusView


async def _producer(watcher: Watcher, package_ahriman: Package) -> None:
    """
    create producer

    Args:
        watcher(Watcher): watcher test instance
        package_ahriman(Package): package test instance
    """
    await asyncio.sleep(0.1)
    await watcher.event_bus.broadcast(EventType.PackageRemoved, package_ahriman.base)
    await watcher.event_bus.broadcast(EventType.PackageUpdated, package_ahriman.base, status="success")
    await asyncio.sleep(0.1)
    await watcher.event_bus.shutdown()


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await EventBusView.get_permission(request) == UserAccess.Full


def test_routes() -> None:
    """
    must return correct routes
    """
    assert EventBusView.ROUTES == ["/api/v1/events/stream"]


async def test_run_timeout() -> None:
    """
    must handle timeout and continue loop
    """
    queue = Queue()

    async def _shutdown() -> None:
        await asyncio.sleep(0.05)
        await queue.put(None)

    response = AsyncMock()
    response.is_connected = lambda: True
    response.ping_interval = 0.01

    asyncio.create_task(_shutdown())
    await EventBusView._run(response, queue)


async def test_get(client: TestClient, package_ahriman: Package) -> None:
    """
    must stream events via SSE
    """
    watcher = next(iter(client.app[WatcherKey].values()))
    asyncio.create_task(_producer(watcher, package_ahriman))
    request_schema = pytest.helpers.schema_request(EventBusView.get, location="querystring")
    # no content validation here because it is a streaming response

    assert not request_schema.validate({})
    response = await client.get("/api/v1/events/stream")
    assert response.status == 200

    body = await response.text()
    assert EventType.PackageUpdated in body
    assert "ahriman" in body


async def test_get_with_topic_filter(client: TestClient, package_ahriman: Package) -> None:
    """
    must filter events by topic
    """
    watcher = next(iter(client.app[WatcherKey].values()))
    asyncio.create_task(_producer(watcher, package_ahriman))
    request_schema = pytest.helpers.schema_request(EventBusView.get, location="querystring")

    payload = {"event": [EventType.PackageUpdated]}
    assert not request_schema.validate(payload)
    response = await client.get("/api/v1/events/stream", params=payload)
    assert response.status == 200

    body = await response.text()
    assert EventType.PackageUpdated in body
    assert EventType.PackageRemoved not in body


async def test_get_with_object_id_filter(client: TestClient, package_ahriman: Package) -> None:
    """
    must filter events by object_id
    """
    watcher = next(iter(client.app[WatcherKey].values()))
    asyncio.create_task(_producer(watcher, package_ahriman))
    request_schema = pytest.helpers.schema_request(EventBusView.get, location="querystring")

    payload = {"object_id": "non-existent-package"}
    assert not request_schema.validate(payload)
    response = await client.get("/api/v1/events/stream", params=payload)
    assert response.status == 200

    body = await response.text()
    assert "ahriman" not in body


async def test_get_bad_request(client: TestClient) -> None:
    """
    must return bad request for invalid event type
    """
    response_schema = pytest.helpers.schema_response(EventBusView.get, code=400)

    response = await client.get("/api/v1/events/stream", params={"event": "invalid"})
    assert response.status == 400
    assert not response_schema.validate(await response.json())


async def test_get_not_found(client: TestClient) -> None:
    """
    must return not found for unknown repository
    """
    response_schema = pytest.helpers.schema_response(EventBusView.get, code=404)

    response = await client.get("/api/v1/events/stream", params={"architecture": "unknown", "repository": "unknown"})
    assert response.status == 404
    assert not response_schema.validate(await response.json())


async def test_get_connection_reset(client: TestClient, mocker: MockerFixture) -> None:
    """
    must handle connection reset
    """
    mocker.patch.object(EventBusView, "_run", side_effect=ConnectionResetError)
    response = await client.get("/api/v1/events/stream")
    assert response.status == 200
