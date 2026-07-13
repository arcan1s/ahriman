from ahriman.core.formatters import ConfigurationPrinter


def test_properties(configuration_printer: ConfigurationPrinter) -> None:
    """
    must return non-empty properties list
    """
    assert configuration_printer.properties()


def test_properties_required(configuration_printer: ConfigurationPrinter) -> None:
    """
    must return all safe properties as required
    """
    assert all(prop.is_required for prop in configuration_printer.properties())

    configuration_printer.values = {"password": "pa55w0rd"}
    assert all(not prop.is_required for prop in configuration_printer.properties())


def test_title(configuration_printer: ConfigurationPrinter) -> None:
    """
    must return non-empty title
    """
    assert configuration_printer.title() == "[section]"
