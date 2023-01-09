from pytest_mock import MockerFixture
from unittest.mock import MagicMock, call as MockCall

from ahriman.core.formatters import PackagePrinter
from ahriman.core.formatters import Printer
from ahriman.models.property import Property


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


def test_print_indent(mocker: MockerFixture) -> None:
    """
    must correctly use indentation
    """
    log_mock = MagicMock()

    mocker.patch("ahriman.core.formatters.Printer.properties", return_value=[Property("key", "value", indent=0)])
    Printer().print(verbose=True, log_fn=log_mock)

    mocker.patch("ahriman.core.formatters.Printer.properties", return_value=[Property("key", "value", indent=1)])
    Printer().print(verbose=True, log_fn=log_mock)

    mocker.patch("ahriman.core.formatters.Printer.properties", return_value=[Property("key", "value", indent=2)])
    Printer().print(verbose=True, log_fn=log_mock)

    log_mock.assert_has_calls([MockCall("key: value"), MockCall("\tkey: value"), MockCall("\t\tkey: value")])


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
