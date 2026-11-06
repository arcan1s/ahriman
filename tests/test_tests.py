from pathlib import Path

from ahriman.core.utils import walk


def _test_path(source_root: Path, source_file: Path) -> Path:
    """
    generate expected test path for source file

    Args:
        source_root(Path): package source root
        source_file(Path): source file

    Returns:
        Path: expected test file path
    """
    relative_path = source_file.relative_to(source_root)

    match relative_path.parts:
        # some workaround for well known files
        case ("ahriman", "application", "handlers", *_, source_name) if source_name != "handler.py":
            return relative_path.parent / f"test_handler_{source_name}"
        case ("ahriman", "web", "views", "api", source_name):
            return relative_path.parent / f"test_view_api_{source_name}"
        case ("ahriman", "web", "views", version, api, source_name) if version in ("v1", "v2"):
            return relative_path.parent / f"test_view_{version}_{api}_{source_name}"
        case ("ahriman", "web", "views", *_, source_name):
            if source_name.endswith("_guard.py"):
                return relative_path.parent / f"test_{source_name}"
            else:
                return relative_path.parent / f"test_view_{source_name}"
        case (*_, source_name) if source_name.startswith("__"):
            return relative_path.parent / f"test_{source_name.replace("__", "")}"
        case _:
            return relative_path.parent / f"test_{source_file.name}"


def test_test_coverage() -> None:
    """
    must have test files for each source file
    """
    def filter_files(filename: str) -> bool:
        return filename.suffix == ".py" \
            and filename.name not in ("__init__.py",)

    package_roots = [
        Path("ahriman-core"),
        Path("ahriman-triggers"),
        Path("ahriman-web"),
    ]

    for package_root in package_roots:
        source_root = package_root / "src"

        for source_file in filter(filter_files, walk(source_root)):
            test_file = package_root / "tests" / _test_path(source_root, source_file)
            assert test_file.is_file(), test_file
