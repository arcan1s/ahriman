from unittest.mock import MagicMock

from ahriman.core.formatters import PackagePrinter
from ahriman.core.formatters import Printer


def test_print(package_ahriman_printer: PackagePrinter) -> None:
    """
    must print content
    """
    log_mock = MagicMock()
    package_ahriman_printer.print(verbose=False, log_fn=log_mock)
    log_mock.assert_called()


def test_print_empty() -> None:
    """
    must not print empty object
    """
    log_mock = MagicMock()
    Printer().print(verbose=True, log_fn=log_mock)
    log_mock.assert_not_called()


def test_print_verbose(package_ahriman_printer: PackagePrinter) -> None:
    """
    must print content with increased verbosity
    """
    log_mock = MagicMock()
    package_ahriman_printer.print(verbose=True, log_fn=log_mock)
    log_mock.assert_called()


def test_properties() -> None:
    """
    must return empty properties list
    """
    assert Printer().properties() == []


def test_title() -> None:
    """
    must return empty title
    """
    assert Printer().title() is None
