from pathlib import Path

from ahriman.models.scan_paths import ScanPaths


def test_is_allowed() -> None:
    """
    must check if path is subpath of one in allowed list
    """
    assert ScanPaths(["usr"]).is_allowed(Path("usr"))
    assert ScanPaths(["usr"]).is_allowed(Path("usr") / "lib")
    assert not ScanPaths(["usr"]).is_allowed(Path("var"))

    assert ScanPaths(["usr(?!/lib)"]).is_allowed(Path("usr"))
    assert ScanPaths(["usr(?!/lib)", "var"]).is_allowed(Path("var"))
    assert not ScanPaths(["usr(?!/lib)"]).is_allowed(Path("usr") / "lib")


def test_is_allowed_default(scan_paths: ScanPaths) -> None:
    """
    must provide expected default configuration
    """
    assert not scan_paths.is_allowed(Path("usr"))
    assert not scan_paths.is_allowed(Path("var"))

    assert scan_paths.is_allowed(Path("usr") / "lib")
    assert scan_paths.is_allowed(Path("usr") / "lib" / "libm.so")

    # cmake case
    assert scan_paths.is_allowed(Path("usr") / "lib" / "libcmake.so")
    assert not scan_paths.is_allowed(Path("usr") / "lib" / "cmake")
    assert not scan_paths.is_allowed(Path("usr") / "lib" / "cmake" / "file.cmake")
