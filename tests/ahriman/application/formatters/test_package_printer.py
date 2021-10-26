from ahriman.application.formatters.package_printer import PackagePrinter


def test_properties(package_ahriman_printer: PackagePrinter) -> None:
    """
    must return non empty properties list
    """
    assert package_ahriman_printer.properties()


def test_title(package_ahriman_printer: PackagePrinter) -> None:
    """
    must return non empty title
    """
    assert package_ahriman_printer.title() is not None
