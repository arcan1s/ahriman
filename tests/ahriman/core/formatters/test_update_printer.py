from ahriman.core.formatters import UpdatePrinter


def test_properties(update_printer: UpdatePrinter) -> None:
    """
    must return non-empty properties list
    """
    assert update_printer.properties()


def test_title(update_printer: UpdatePrinter) -> None:
    """
    must return non-empty title
    """
    assert update_printer.title() is not None
