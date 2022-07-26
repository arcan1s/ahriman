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
