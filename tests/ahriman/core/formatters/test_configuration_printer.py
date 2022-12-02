from ahriman.core.formatters import ConfigurationPrinter


def test_properties(configuration_printer: ConfigurationPrinter) -> None:
    """
    must return non-empty properties list
    """
    assert configuration_printer.properties()


def test_properties_required(configuration_printer: ConfigurationPrinter) -> None:
    """
    must return all properties as required
    """
    assert all(prop.is_required for prop in configuration_printer.properties())


def test_title(configuration_printer: ConfigurationPrinter) -> None:
    """
    must return non-empty title
    """
    assert configuration_printer.title() == "[section]"
