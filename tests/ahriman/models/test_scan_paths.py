from pathlib import Path

from ahriman.models.scan_paths import ScanPaths


def test_post_init(scan_paths: ScanPaths) -> None:
    """
    must convert paths to / relative
    """
    assert all(not path.is_absolute() for path in scan_paths.allowed_paths)
    assert all(not path.is_absolute() for path in scan_paths.blacklisted_paths)


def test_is_allowed() -> None:
    """
    must check if path is subpath of one in allowed list
    """
    assert ScanPaths(allowed_paths=[Path("/") / "usr"], blacklisted_paths=[]).is_allowed(Path("usr"))
    assert ScanPaths(allowed_paths=[Path("/") / "usr"], blacklisted_paths=[]).is_allowed(Path("usr") / "lib")
    assert not ScanPaths(allowed_paths=[Path("/") / "usr"], blacklisted_paths=[]).is_allowed(Path("var"))


def test_is_blacklisted() -> None:
    """
    must check if path is not subpath of one in blacklist
    """
    assert ScanPaths(
        allowed_paths=[Path("/") / "usr"],
        blacklisted_paths=[Path("/") / "usr" / "lib"],
    ).is_allowed(Path("usr"))
    assert ScanPaths(
        allowed_paths=[Path("/") / "usr", Path("/") / "var"],
        blacklisted_paths=[Path("/") / "usr" / "lib"],
    ).is_allowed(Path("var"))
    assert not ScanPaths(
        allowed_paths=[Path("/") / "usr"],
        blacklisted_paths=[Path("/") / "usr" / "lib"],
    ).is_allowed(Path(" usr") / "lib")
    assert not ScanPaths(
        allowed_paths=[Path("/") / "usr"],
        blacklisted_paths=[Path("/") / "usr" / "lib"],
    ).is_allowed(Path("usr") / "lib" / "qt")
