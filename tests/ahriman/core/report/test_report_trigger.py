from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.report import ReportTrigger
from ahriman.models.result import Result


def test_configuration_sections(configuration: Configuration) -> None:
    """
    must correctly parse target list
    """
    configuration.set_option("report", "target", "a b c")
    assert ReportTrigger.configuration_sections(configuration) == ["a", "b", "c"]

    configuration.remove_option("report", "target")
    assert ReportTrigger.configuration_sections(configuration) == []


def test_on_result(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run report for specified targets
    """
    configuration.set_option("report", "target", "email")
    run_mock = mocker.patch("ahriman.core.report.report.Report.run")
    _, repository_id = configuration.check_loaded()

    trigger = ReportTrigger(repository_id, configuration)
    trigger.on_result(Result(), [])
    run_mock.assert_called_once_with(Result(), [])
