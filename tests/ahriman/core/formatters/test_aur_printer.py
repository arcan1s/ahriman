from ahriman.core.formatters.aur_printer import AurPrinter


def test_properties(aur_package_ahriman_printer: AurPrinter) -> None:
    """
    must return non empty properties list
    """
    assert aur_package_ahriman_printer.properties()


def test_title(aur_package_ahriman_printer: AurPrinter) -> None:
    """
    must return non empty title
    """
    assert aur_package_ahriman_printer.title() is not None
