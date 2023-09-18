from ahriman.core.formatters import RepositoryPrinter


def test_properties(repository_printer: RepositoryPrinter) -> None:
    """
    must return empty properties list
    """
    assert repository_printer.properties()


def test_title(repository_printer: RepositoryPrinter) -> None:
    """
    must return non-empty title
    """
    assert repository_printer.title() is not None
