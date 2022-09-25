from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.report import ReportTrigger
from ahriman.models.result import Result


def test_on_result(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run report for specified targets
    """
    configuration.set_option("report", "target", "email")
    run_mock = mocker.patch("ahriman.core.report.Report.run")

    trigger = ReportTrigger("x86_64", configuration)
    trigger.on_result(Result(), [])
    run_mock.assert_called_once_with(Result(), [])
