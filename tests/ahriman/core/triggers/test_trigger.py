from unittest.mock import MagicMock

from ahriman.core.triggers import Trigger
from ahriman.models.result import Result


def test_on_result(trigger: Trigger) -> None:
    """
    must pass execution nto run method
    """
    trigger.on_result(Result(), [])


def test_on_result_run(trigger: Trigger) -> None:
    """
    must fallback to run method if it exists
    """
    run_mock = MagicMock()
    setattr(trigger, "run", run_mock)

    trigger.on_result(Result(), [])
    run_mock.assert_called_once_with(Result(), [])


def test_on_start(trigger: Trigger) -> None:
    """
    must do nothing for not implemented method on_start
    """
    trigger.on_start()


def test_on_stop(trigger: Trigger) -> None:
    """
    must do nothing for not implemented method on_stop
    """
    trigger.on_stop()
