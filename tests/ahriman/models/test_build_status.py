from ahriman.models.build_status import BuildStatus, BuildStatusEnum


def test_build_status_enum_badges_color() -> None:
    """
    status color must be one of shields.io supported
    """
    SUPPORTED_COLORS = [
        "brightgreen", "green", "yellowgreen", "yellow", "orange", "red", "blue", "lightgrey",
        "success", "important", "critical", "informational", "inactive", "blueviolet"
    ]

    for status in BuildStatusEnum:
        assert status.badges_color() in SUPPORTED_COLORS


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


def test_build_status_from_json_view(build_status_failed: BuildStatus) -> None:
    """
    must construct same object from json
    """
    assert BuildStatus.from_json(build_status_failed.view()) == build_status_failed
