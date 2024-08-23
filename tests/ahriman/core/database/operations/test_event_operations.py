from ahriman.core.database import SQLite
from ahriman.models.event import Event, EventType
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId


def test_event_insert_get(database: SQLite, package_ahriman: Package) -> None:
    """
    must insert and get event
    """
    event = Event(EventType.PackageUpdated, package_ahriman.base, "Updated", {"key": "value"})
    database.event_insert(event)
    assert database.event_get() == [event]

    event2 = Event("event", "object")
    database.event_insert(event2, RepositoryId("i686", database._repository_id.name))
    assert database.event_get() == [event]
    assert database.event_get(repository_id=RepositoryId("i686", database._repository_id.name)) == [event2]


def test_event_insert_get_filter(database: SQLite) -> None:
    """
    must insert and get events with filter
    """
    database.event_insert(Event("event 1", "object 1", created=1))
    database.event_insert(Event("event 2", "object 2"))
    database.event_insert(Event(EventType.PackageUpdated, "package"))

    assert database.event_get(event="event 1") == [Event("event 1", "object 1", created=1)]
    assert database.event_get(object_id="object 1") == [Event("event 1", "object 1", created=1)]
    assert all(event.event == EventType.PackageUpdated for event in database.event_get(event=EventType.PackageUpdated))


def test_event_insert_get_pagination(database: SQLite) -> None:
    """
    must insert and get events with pagination
    """
    database.event_insert(Event("1", "1"))
    database.event_insert(Event("2", "2"))
    assert all(event.event == "2" for event in database.event_get(limit=1, offset=1))
