from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.distributed import WorkerTrigger


def test_on_start(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must register itself as worker
    """
    configuration.set_option("status", "address", "http://localhost:8081")
    run_mock = mocker.patch("ahriman.core.distributed.WorkerTrigger.register")
    _, repository_id = configuration.check_loaded()

    trigger = WorkerTrigger(repository_id, configuration)
    trigger.on_start()
    run_mock.assert_called_once_with()


def test_on_stop(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must unregister itself as worker
    """
    configuration.set_option("status", "address", "http://localhost:8081")
    run_mock = mocker.patch("ahriman.core.distributed.WorkerTrigger.unregister")
    _, repository_id = configuration.check_loaded()

    trigger = WorkerTrigger(repository_id, configuration)
    trigger.on_stop()
    run_mock.assert_called_once_with()
