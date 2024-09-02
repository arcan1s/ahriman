from ahriman.core.formatters import PackageStatsPrinter


def test_properties(package_stats_printer: PackageStatsPrinter) -> None:
    """
    must return non-empty properties list
    """
    assert package_stats_printer.properties()


def test_properties_sorted(package_stats_printer: PackageStatsPrinter) -> None:
    """
    properties list must be sorted in descending order
    """
    prop1, prop2 = package_stats_printer.properties()
    assert prop1.value > prop2.value


def test_properties_empty() -> None:
    """
    must return empty properties list for the empty events list
    """
    assert not PackageStatsPrinter({}).properties()


def test_title(package_stats_printer: PackageStatsPrinter) -> None:
    """
    must return non-empty title
    """
    assert package_stats_printer.title() is not None
