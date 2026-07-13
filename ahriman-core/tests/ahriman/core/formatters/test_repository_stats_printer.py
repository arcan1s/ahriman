from ahriman.core.formatters import RepositoryStatsPrinter


def test_properties(repository_stats_printer: RepositoryStatsPrinter) -> None:
    """
    must return non-empty properties list
    """
    assert repository_stats_printer.properties()


def test_title(repository_stats_printer: RepositoryStatsPrinter) -> None:
    """
    must return non-empty title
    """
    assert repository_stats_printer.title()
