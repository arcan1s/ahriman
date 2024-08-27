import pytest

from aiohttp.test_utils import TestClient

from ahriman.models.event import Event
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.auditlog.events import EventsView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET", "POST"):
        request = pytest.helpers.request("", "", method)
        assert await EventsView.get_permission(request) == UserAccess.Full


def test_routes() -> None:
    """
    must return correct routes
    """
    assert EventsView.ROUTES == ["/api/v1/events"]


async def test_get(client: TestClient) -> None:
    """
    must return all events
    """
    event1 = Event("event1", "object1", "message", key="value")
    event2 = Event("event2", "object2")
    await client.post("/api/v1/events", json=event1.view())
    await client.post("/api/v1/events", json=event2.view())
    response_schema = pytest.helpers.schema_response(EventsView.get)

    response = await client.get("/api/v1/events")
    assert response.ok
    json = await response.json()
    assert not response_schema.validate(json, many=True)

    events = [Event.from_json(event) for event in json]
    assert events == [event1, event2]


async def test_get_with_pagination(client: TestClient) -> None:
    """
    must get events with pagination
    """
    event1 = Event("event1", "object1", "message", key="value")
    event2 = Event("event2", "object2")
    await client.post("/api/v1/events", json=event1.view())
    await client.post("/api/v1/events", json=event2.view())
    request_schema = pytest.helpers.schema_request(EventsView.get, location="querystring")
    response_schema = pytest.helpers.schema_response(EventsView.get)

    payload = {"limit": 1, "offset": 1}
    assert not request_schema.validate(payload)
    response = await client.get("/api/v1/events", params=payload)
    assert response.status == 200

    json = await response.json()
    assert not response_schema.validate(json, many=True)

    assert [Event.from_json(event) for event in json] == [event2]


async def test_get_bad_request(client: TestClient) -> None:
    """
    must return bad request for invalid query parameters
    """
    response_schema = pytest.helpers.schema_response(EventsView.get, code=400)

    response = await client.get("/api/v1/events", params={"limit": "limit"})
    assert response.status == 400
    assert not response_schema.validate(await response.json())

    response = await client.get("/api/v1/events", params={"offset": "offset"})
    assert response.status == 400
    assert not response_schema.validate(await response.json())


async def test_post(client: TestClient) -> None:
    """
    must create event
    """
    event = Event("event1", "object1", "message", key="value")
    request_schema = pytest.helpers.schema_request(EventsView.post)

    payload = event.view()
    assert not request_schema.validate(payload)

    response = await client.post("/api/v1/events", json=payload)
    assert response.status == 204


async def test_post_exception(client: TestClient) -> None:
    """
    must raise exception on invalid payload
    """
    response_schema = pytest.helpers.schema_response(EventsView.post, code=400)

    response = await client.post("/api/v1/events", json={})
    assert response.status == 400
    assert not response_schema.validate(await response.json())
