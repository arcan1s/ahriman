from pathlib import Path

from ahriman.core.utils import walk


def test_test_coverage() -> None:
    """
    must have test files for each source file
    """
    package_roots = [
        Path("ahriman-core"),
        Path("ahriman-triggers"),
        Path("ahriman-web"),
    ]

    for package_root in package_roots:
        source_root = package_root / "src"

        for source_file in filter(lambda fn: fn.suffix == ".py" and fn.name != "__init__.py", walk(source_root)):
            test_file = package_root / "tests" / _test_path(source_root, source_file)
            assert test_file.is_file(), test_file


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
        case ("ahriman", "application", "handlers", *_, filename) if filename != "handler.py":
            filename = f"test_handler_{source_file.name}"
            test_parent = Path("ahriman", "application", "handlers")
        case ("ahriman", "web", "views", _, filename) if (api := relative_path.parts[3]) == "api":
            filename = f"test_view_{api}_{source_file.name}"
            test_parent = relative_path.parent
        case ("ahriman", "web", "views", _, _, filename) if (version := relative_path.parts[3]) in ("v1", "v2"):
            api = relative_path.parts[4]
            filename = f"test_view_{version}_{api}_{source_file.name}"
            test_parent = relative_path.parent
        case ("ahriman", "web", "views", *_, filename):
            if source_file.name.endswith("_guard.py"):
                filename = f"test_{source_file.name}"
            else:
                filename = f"test_view_{source_file.name}"
            test_parent = relative_path.parent
        case _:
            filename = f"test_{source_file.name}"
            test_parent = relative_path.parent

    return test_parent / filename
