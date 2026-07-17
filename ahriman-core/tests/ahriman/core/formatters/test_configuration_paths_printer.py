from ahriman.core.formatters import ConfigurationPathsPrinter


def test_properties(configuration_paths_printer: ConfigurationPathsPrinter) -> None:
    """
    must return non-empty properties list
    """
    assert configuration_paths_printer.properties()


def test_title(configuration_paths_printer: ConfigurationPathsPrinter) -> None:
    """
    must return non-empty title
    """
    assert configuration_paths_printer.title() is not None
