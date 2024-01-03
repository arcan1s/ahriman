from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.distributed import WorkerTrigger


def test_on_start(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must register itself as worker
    """
    configuration.set_option("status", "address", "http://localhost:8081")
    run_mock = mocker.patch("threading.Timer.start")
    _, repository_id = configuration.check_loaded()

    WorkerTrigger(repository_id, configuration).on_start()
    run_mock.assert_called_once_with()


def test_on_stop(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must unregister itself as worker
    """
    configuration.set_option("status", "address", "http://localhost:8081")
    run_mock = mocker.patch("threading.Timer.cancel")
    _, repository_id = configuration.check_loaded()

    WorkerTrigger(repository_id, configuration).on_stop()
    run_mock.assert_called_once_with()


def test_on_stop_empty_timer(configuration: Configuration) -> None:
    """
    must do not fail if no timer was started
    """
    configuration.set_option("status", "address", "http://localhost:8081")
    _, repository_id = configuration.check_loaded()

    WorkerTrigger(repository_id, configuration).on_stop()


def test_ping(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must correctly process timer action
    """
    configuration.set_option("status", "address", "http://localhost:8081")
    run_mock = mocker.patch("ahriman.core.distributed.WorkerTrigger.register")
    timer_mock = mocker.patch("threading.Timer.start")
    _, repository_id = configuration.check_loaded()

    WorkerTrigger(repository_id, configuration).ping()
    run_mock.assert_called_once_with()
    timer_mock.assert_called_once_with()
