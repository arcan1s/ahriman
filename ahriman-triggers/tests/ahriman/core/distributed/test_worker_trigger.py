from pytest_mock import MockerFixture
from threading import Timer

from ahriman.core.distributed import WorkerTrigger


def test_create_timer(worker_trigger: WorkerTrigger) -> None:
    """
    must create a timer and put it to queue
    """
    worker_trigger.create_timer()
    assert worker_trigger._timer.function == worker_trigger.ping
    worker_trigger._timer.cancel()


def test_on_start(worker_trigger: WorkerTrigger, mocker: MockerFixture) -> None:
    """
    must register itself as worker
    """
    run_mock = mocker.patch("ahriman.core.distributed.WorkerTrigger.create_timer")
    worker_trigger.on_start()
    run_mock.assert_called_once_with()


def test_on_stop(worker_trigger: WorkerTrigger, mocker: MockerFixture) -> None:
    """
    must unregister itself as worker
    """
    run_mock = mocker.patch("threading.Timer.cancel")
    worker_trigger._timer = Timer(1, print)  # doesn't matter

    worker_trigger.on_stop()
    run_mock.assert_called_once_with()


def test_on_stop_empty_timer(worker_trigger: WorkerTrigger) -> None:
    """
    must do not fail if no timer was started
    """
    worker_trigger.on_stop()


def test_ping(worker_trigger: WorkerTrigger, mocker: MockerFixture) -> None:
    """
    must correctly process timer action
    """
    run_mock = mocker.patch("ahriman.core.distributed.WorkerTrigger.register")
    timer_mock = mocker.patch("threading.Timer.start")
    worker_trigger._timer = Timer(1, print)  # doesn't matter

    worker_trigger.ping()
    run_mock.assert_called_once_with()
    timer_mock.assert_called_once_with()


def test_ping_empty_queue(worker_trigger: WorkerTrigger, mocker: MockerFixture) -> None:
    """
    must do nothing in case of empty queue
    """
    run_mock = mocker.patch("ahriman.core.distributed.WorkerTrigger.register")
    worker_trigger.ping()
    run_mock.assert_not_called()
