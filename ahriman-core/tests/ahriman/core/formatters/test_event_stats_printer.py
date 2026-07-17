from ahriman.core.formatters import EventStatsPrinter


def test_properties(event_stats_printer: EventStatsPrinter) -> None:
    """
    must return empty properties list
    """
    assert event_stats_printer.properties()


def test_properties_empty() -> None:
    """
    must correctly generate properties for empty events list
    """
    assert EventStatsPrinter("event", []).properties()


def test_title(event_stats_printer: EventStatsPrinter) -> None:
    """
    must return non-empty title
    """
    assert event_stats_printer.title() is not None
