from pytest_mock import MockerFixture
from unittest import mock

from ahriman.core.configuration import Configuration
from ahriman.core.report import Console
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_generate(configuration: Configuration, result: Result, package_python_schedule: Package,
                  mocker: MockerFixture) -> None:
    """
    must print result to stdout
    """
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")
    result.add_failed(package_python_schedule)
    report = Console("x86_64", configuration, "console")

    report.generate([], result)
    print_mock.assert_has_calls([mock.call(verbose=True), mock.call(verbose=True)])
