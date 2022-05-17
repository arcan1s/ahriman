import datetime
import time

from ahriman.models.build_status import BuildStatus, BuildStatusEnum


def test_build_status_init_1() -> None:
    """
    must construct status object from None
    """
    status = BuildStatus()
    assert status.status == BuildStatusEnum.Unknown
    assert status.timestamp > 0


def test_build_status_init_2(build_status_failed: BuildStatus) -> None:
    """
    must construct status object from objects
    """
    status = BuildStatus(BuildStatusEnum.Failed, 42)
    assert status == build_status_failed


def test_build_status_init_empty_timestamp() -> None:
    """
    must st current timestamp when not set
    """
    first = BuildStatus()
    time.sleep(1)
    second = BuildStatus()
    # well technically it just should increase
    assert first.timestamp < second.timestamp


def test_build_status_from_json_view(build_status_failed: BuildStatus) -> None:
    """
    must construct same object from json
    """
    assert BuildStatus.from_json(build_status_failed.view()) == build_status_failed


def test_build_status_pretty_print(build_status_failed: BuildStatus) -> None:
    """
    must return string in pretty print function
    """
    assert build_status_failed.pretty_print()
    assert isinstance(build_status_failed.pretty_print(), str)


def test_build_status_eq(build_status_failed: BuildStatus) -> None:
    """
    must be equal
    """
    other = BuildStatus.from_json(build_status_failed.view())
    assert other == build_status_failed


def test_build_status_eq_self(build_status_failed: BuildStatus) -> None:
    """
    must be equal itself
    """
    assert build_status_failed == build_status_failed


def test_build_status_ne_by_status(build_status_failed: BuildStatus) -> None:
    """
    must be not equal by status
    """
    other = BuildStatus.from_json(build_status_failed.view())
    other.status = BuildStatusEnum.Success
    assert build_status_failed != other


def test_build_status_ne_by_timestamp(build_status_failed: BuildStatus) -> None:
    """
    must be not equal by timestamp
    """
    other = BuildStatus.from_json(build_status_failed.view())
    other.timestamp = datetime.datetime.utcnow().timestamp()
    assert build_status_failed != other


def test_build_status_ne_other(build_status_failed: BuildStatus) -> None:
    """
    must be not equal to random object
    """
    assert build_status_failed != object()


def test_build_status_repr(build_status_failed: BuildStatus) -> None:
    """
    must return string in __repr__ function
    """
    assert build_status_failed.__repr__()
    assert isinstance(build_status_failed.__repr__(), str)
