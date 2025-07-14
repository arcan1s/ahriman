from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.configuration import Configuration
from ahriman.core.housekeeping import LogsRotationTrigger
from ahriman.core.status import Client
from ahriman.models.result import Result


def test_configuration_sections(configuration: Configuration) -> None:
    """
    must correctly parse target list
    """
    assert LogsRotationTrigger.configuration_sections(configuration) == ["logs-rotation"]


def test_rotate(logs_rotation_trigger: LogsRotationTrigger, mocker: MockerFixture) -> None:
    """
    must rotate logs
    """
    client_mock = MagicMock()
    context_mock = mocker.patch("ahriman.core._Context.get", return_value=client_mock)

    logs_rotation_trigger.on_result(Result(), [])
    context_mock.assert_called_once_with(Client)
    client_mock.logs_rotate.assert_called_once_with(logs_rotation_trigger.keep_last_records)
