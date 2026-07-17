from ahriman.core.formatters import UpdatePrinter
from ahriman.models.property import Property


def test_properties(update_printer: UpdatePrinter) -> None:
    """
    must return non-empty properties list
    """
    assert update_printer.properties()


def test_properties_na(update_printer: UpdatePrinter) -> None:
    """
    must return N/A if local version is unknown
    """
    assert update_printer.properties() == [Property("N/A", update_printer.package.version, is_required=True)]


def test_properties_bump_pkgrel(update_printer: UpdatePrinter) -> None:
    """
    must bump pkgrel if local version is the same
    """
    update_printer.local_version = update_printer.package.version
    assert update_printer.properties() == [Property(update_printer.package.version, "2.6.0-1.1", is_required=True)]


def test_properties_keep_pkgrel(update_printer: UpdatePrinter) -> None:
    """
    must keep pkgrel if local version is not the same
    """
    update_printer.local_version = "2.5.0-1"
    assert update_printer.properties() == [
        Property(update_printer.local_version, update_printer.package.version, is_required=True),
    ]


def test_title(update_printer: UpdatePrinter) -> None:
    """
    must return non-empty title
    """
    assert update_printer.title() is not None
