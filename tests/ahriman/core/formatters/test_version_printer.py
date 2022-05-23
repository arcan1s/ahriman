from ahriman.core.formatters import VersionPrinter


def test_properties(version_printer: VersionPrinter) -> None:
    """
    must return empty properties list
    """
    assert version_printer.properties()


def test_title(version_printer: VersionPrinter) -> None:
    """
    must return non empty title
    """
    assert version_printer.title() is not None
