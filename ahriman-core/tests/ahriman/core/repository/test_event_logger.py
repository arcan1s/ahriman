import pytest

from pytest_mock import MockerFixture

from ahriman.core.repository.event_logger import EventLogger
from ahriman.models.event import Event, EventType


def test_event(repository: EventLogger, mocker: MockerFixture) -> None:
    """
    must log event
    """
    event = Event(EventType.PackageUpdated, "base", "message", created=pytest.helpers.anyvar(int, True))
    event_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.event_add")

    repository.event(event.object_id, event.event, event.message)
    event_mock.assert_called_once_with(event)


def test_in_event(repository: EventLogger, mocker: MockerFixture) -> None:
    """
    must log success action
    """
    event = Event(EventType.PackageUpdated, "base", "message",
                  created=pytest.helpers.anyvar(int, True), took=pytest.helpers.anyvar(float, True))
    event_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.event_add")

    with repository.in_event(event.object_id, event.event, event.message):
        pass
    event_mock.assert_called_once_with(event)


def test_in_event_exception(repository: EventLogger, mocker: MockerFixture) -> None:
    """
    must reraise exception in context
    """
    event = Event(EventType.PackageUpdated, "base", "message",
                  created=pytest.helpers.anyvar(int, True), took=pytest.helpers.anyvar(float, True))
    event_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.event_add")

    with pytest.raises(Exception):
        with repository.in_event(event.object_id, event.event, event.message):
            raise Exception
    event_mock.assert_not_called()


def test_in_event_exception_event(repository: EventLogger, mocker: MockerFixture) -> None:
    """
    must reraise exception in context and emit new event
    """
    event = Event(EventType.PackageUpdateFailed, "base", created=pytest.helpers.anyvar(int, True),
                  took=pytest.helpers.anyvar(float, True))
    event_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.event_add")

    with pytest.raises(Exception):
        with repository.in_event(event.object_id, EventType.PackageUpdated, failure=event.event):
            raise Exception
    event_mock.assert_called_once_with(event)
