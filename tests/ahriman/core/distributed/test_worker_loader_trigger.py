from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.distributed import WorkerLoaderTrigger
from ahriman.models.worker import Worker


def test_on_start(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must load workers from remote
    """
    worker = Worker("address")
    configuration.set_option("status", "address", "http://localhost:8081")
    run_mock = mocker.patch("ahriman.core.distributed.WorkerLoaderTrigger.workers", return_value=[worker])
    _, repository_id = configuration.check_loaded()

    trigger = WorkerLoaderTrigger(repository_id, configuration)
    trigger.on_start()
    run_mock.assert_called_once_with()
    assert configuration.getlist("build", "workers") == [worker.address]


def test_on_start_skip(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must skip loading if option is already set
    """
    configuration.set_option("status", "address", "http://localhost:8081")
    configuration.set_option("build", "workers", "address")
    run_mock = mocker.patch("ahriman.core.distributed.WorkerLoaderTrigger.workers")
    _, repository_id = configuration.check_loaded()

    trigger = WorkerLoaderTrigger(repository_id, configuration)
    trigger.on_start()
    run_mock.assert_not_called()
