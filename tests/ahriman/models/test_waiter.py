import pytest
import time

from ahriman.models.waiter import Waiter, WaiterResult, WaiterTaskFinished, WaiterTimedOut


def test_result_to_float() -> None:
    """
    must convert waiter result to float
    """
    assert float(WaiterResult(4.2)) == 4.2


def test_result_not_implemented() -> None:
    """
    must raise NotImplementedError for abstract class
    """
    with pytest.raises(NotImplementedError):
        assert bool(WaiterResult(4.2))


def test_result_success_to_bool() -> None:
    """
    must convert success waiter result to bool
    """
    assert bool(WaiterTaskFinished(4.2))


def test_result_failure_to_bool() -> None:
    """
    must convert failure waiter result to bool
    """
    assert not bool(WaiterTimedOut(4.2))


def test_is_timed_out() -> None:
    """
    must correctly check if timer runs out
    """
    assert Waiter(-1).is_timed_out()
    assert Waiter(1, start_time=time.monotonic() - 10.0).is_timed_out()
    assert not Waiter(1, start_time=time.monotonic() + 10.0).is_timed_out()


def test_is_timed_out_infinite() -> None:
    """
    must treat 0 wait timeout as infinite
    """
    assert not Waiter(0).is_timed_out()
    assert not Waiter(0, start_time=time.monotonic() - 10.0).is_timed_out()


def test_wait() -> None:
    """
    must wait for success result
    """
    results = iter([True, False])
    waiter = Waiter(1, interval=0.1)
    assert float(waiter.wait(lambda: next(results))) > 0


def test_wait_timeout() -> None:
    """
    must return WaiterTimedOut on timeout
    """
    results = iter([True, False])
    waiter = Waiter(-1, interval=0.1)
    assert isinstance(waiter.wait(lambda: next(results)), WaiterTimedOut)


def test_wait_success() -> None:
    """
    must return WaiterTaskFinished on success
    """
    results = iter([True, False])
    waiter = Waiter(1, interval=0.1)
    assert isinstance(waiter.wait(lambda: next(results)), WaiterTaskFinished)
