from pathlib import Path

from ahriman.core.util import walk


def test_test_coverage() -> None:
    """
    must have test files for each source file
    """
    root = Path()
    for source_file in filter(lambda fn: fn.suffix == ".py" and fn.name != "__init__.py", walk(root / "src")):
        # some workaround for well known files
        if source_file.parts[2:4] == ("application", "handlers") and source_file.name != "handler.py":
            filename = f"test_handler_{source_file.name}"
        elif source_file.parts[2:4] == ("web", "views"):
            if (api := source_file.parts[4]) == "api":
                filename = f"test_view_{api}_{source_file.name}"
            elif (version := source_file.parts[4]) in ("v1", "v2"):
                api = source_file.parts[5]
                filename = f"test_view_{version}_{api}_{source_file.name}"
            else:
                filename = f"test_view_{source_file.name}"
        else:
            filename = f"test_{source_file.name}"

        test_file = Path("tests", *source_file.parts[1:-1], filename)
        assert test_file.is_file(), test_file
