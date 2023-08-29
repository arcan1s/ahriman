from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.core.report.console import Console
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_generate(configuration: Configuration, result: Result, package_python_schedule: Package,
                  mocker: MockerFixture) -> None:
    """
    must print result to stdout
    """
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")
    result.add_failed(package_python_schedule)
    _, repository_id = configuration.check_loaded()
    report = Console(repository_id, configuration, "console")

    report.generate([], result)
    print_mock.assert_has_calls([MockCall(verbose=True), MockCall(verbose=True)])
