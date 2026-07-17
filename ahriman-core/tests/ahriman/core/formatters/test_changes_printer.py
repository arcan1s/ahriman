from ahriman.core.formatters import ChangesPrinter
from ahriman.models.changes import Changes


def test_properties(changes_printer: ChangesPrinter) -> None:
    """
    must return non-empty properties list
    """
    assert changes_printer.properties()


def test_properties_empty() -> None:
    """
    must return empty properties list if change is empty
    """
    assert not ChangesPrinter(Changes()).properties()
    assert not ChangesPrinter(Changes("sha")).properties()


def test_title(changes_printer: ChangesPrinter) -> None:
    """
    must return non-empty title
    """
    assert changes_printer.title()


def test_title_empty() -> None:
    """
    must return empty title if change is empty
    """
    assert not ChangesPrinter(Changes()).title()
    assert not ChangesPrinter(Changes("sha")).title()
