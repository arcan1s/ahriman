from pytest_mock import MockerFixture

from ahriman.core.triggers import Trigger
from ahriman.models.result import Result


def test_on_result(trigger: Trigger, mocker: MockerFixture) -> None:
    """
    must pass execution nto run method
    """
    run_mock = mocker.patch("ahriman.core.triggers.Trigger.run")
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


def test_run(trigger: Trigger) -> None:
    """
    must do nothing for not implemented method run
    """
    trigger.run(Result(), [])
