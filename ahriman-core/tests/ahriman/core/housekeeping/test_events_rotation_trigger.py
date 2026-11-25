from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.configuration import Configuration
from ahriman.core.housekeeping import EventsRotationTrigger
from ahriman.core.status import Client
from ahriman.models.result import Result


def test_configuration_sections(configuration: Configuration) -> None:
    """
    must correctly parse target list
    """
    assert EventsRotationTrigger.configuration_sections(configuration) == ["events-rotation"]


def test_on_result(events_rotation_trigger: EventsRotationTrigger, mocker: MockerFixture) -> None:
    """
    must rotate events
    """
    client_mock = MagicMock()
    context_mock = mocker.patch("ahriman.core._Context.get", return_value=client_mock)

    events_rotation_trigger.on_result(Result(), [])
    context_mock.assert_called_once_with(Client)
    client_mock.events_rotate.assert_called_once_with(events_rotation_trigger.keep_last_records)
