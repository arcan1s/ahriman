from ahriman.core.formatters import PkgbuildPrinter
from ahriman.models.changes import Changes


def test_properties(pkgbuild_printer: PkgbuildPrinter) -> None:
    """
    must return non-empty properties list
    """
    assert pkgbuild_printer.properties()


def test_properties_empty() -> None:
    """
    must return empty properties list if pkgbuild is empty
    """
    assert not PkgbuildPrinter(Changes()).properties()
    assert not PkgbuildPrinter(Changes("sha", "changes")).properties()


def test_title(pkgbuild_printer: PkgbuildPrinter) -> None:
    """
    must return non-empty title
    """
    assert pkgbuild_printer.title()


def test_title_empty() -> None:
    """
    must return empty title if change is empty
    """
    assert not PkgbuildPrinter(Changes()).title()
    assert not PkgbuildPrinter(Changes("sha")).title()
