from ahriman.core.formatters.string_printer import StringPrinter


def test_properties(string_printer: StringPrinter) -> None:
    """
    must return empty properties list
    """
    assert not string_printer.properties()


def test_title(string_printer: StringPrinter) -> None:
    """
    must return non empty title
    """
    assert string_printer.title() is not None
