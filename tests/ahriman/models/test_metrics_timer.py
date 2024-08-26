import pytest
import time

from ahriman.core.exceptions import InitializeError
from ahriman.models.metrics_timer import MetricsTimer


def test_elapsed() -> None:
    """
    must return elapsed time
    """
    with MetricsTimer() as timer:
        value1 = timer.elapsed
        time.sleep(0.1)
        value2 = timer.elapsed
        assert value2 > value1


def test_elapsed_exception() -> None:
    """
    must raise InitializeError if timer wasn't started in the context manager
    """
    timer = MetricsTimer()
    with pytest.raises(InitializeError):
        assert timer.elapsed


def test_enter() -> None:
    """
    must start timer with context manager
    """
    with MetricsTimer() as timer:
        assert timer.start_time > 0


def test_exit_with_exception() -> None:
    """
    must exit from context manager if an exception is raised
    """
    with pytest.raises(ValueError):
        with MetricsTimer():
            raise ValueError()
