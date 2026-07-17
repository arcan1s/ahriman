from ahriman.models.event import Event, EventType


def test_init() -> None:
    """
    must replace event type for known types
    """
    assert Event("random", "")
    assert isinstance(Event(str(EventType.PackageUpdated), "").event, EventType)

    assert Event("", "", key="value").data == {"key": "value"}

    assert Event("", "").created > 0


def test_from_json_view() -> None:
    """
    must construct and serialize event to json
    """
    event = Event("event", "object", "message", key="value")
    assert Event.from_json(event.view()) == event


def test_get() -> None:
    """
    must return property correctly
    """
    assert Event("event", "object", "message", key="value").get("key") == "value"
    assert Event("event", "object").get("key") is None


def test_view_empty() -> None:
    """
    must skip empty fields during (de-)serialization
    """
    event = Event("event", "object")
    assert Event.from_json(event.view()) == event
    assert "message" not in event.view()
    assert "data" not in event.view()


def test_eq() -> None:
    """
    must compare two events
    """
    event1 = Event("1", "1", "1", 1, key="value")
    assert event1 == event1

    event2 = Event("2", "2", "2", 2, key="value")
    assert event1 != event2


def test_eq_other() -> None:
    """
    must return False in case if object is not an instance of event
    """
    assert Event("1", "1") != 42
