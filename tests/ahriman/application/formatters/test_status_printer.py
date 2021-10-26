from ahriman.application.formatters.status_printer import StatusPrinter


def test_properties(status_printer: StatusPrinter) -> None:
    """
    must return empty properties list
    """
    assert not status_printer.properties()


def test_title(status_printer: StatusPrinter) -> None:
    """
    must return non empty title
    """
    assert status_printer.title() is not None
