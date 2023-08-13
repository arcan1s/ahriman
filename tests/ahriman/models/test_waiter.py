import time

from ahriman.models.waiter import Waiter


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
    must wait until file will disappear
    """
    results = iter([True, False])
    waiter = Waiter(1, interval=1)
    assert waiter.wait(lambda: next(results)) > 0
