from ahriman.models.event import Event, EventType


def test_post_init() -> None:
    """
    must remove replace empty dictionary
    """
    assert Event("", "").data == {}
    assert isinstance(Event(str(EventType.PackageUpdated), "").event, EventType)


def test_from_json_view() -> None:
    """
    must construct and serialize event to json
    """
    event = Event("event", "object", "message", {"key": "value"})
    assert Event.from_json(event.view()) == event
