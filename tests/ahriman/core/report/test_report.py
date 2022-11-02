import pytest

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import ReportFailed
from ahriman.core.report.report import Report
from ahriman.models.report_settings import ReportSettings
from ahriman.models.result import Result


def test_report_failure(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must raise ReportFailed on errors
    """
    mocker.patch("ahriman.core.report.html.HTML.generate", side_effect=Exception())
    with pytest.raises(ReportFailed):
        Report.load("x86_64", configuration, "html").run(Result(), [])


def test_report_dummy(configuration: Configuration, result: Result, mocker: MockerFixture) -> None:
    """
    must construct dummy report class
    """
    mocker.patch("ahriman.models.report_settings.ReportSettings.from_option", return_value=ReportSettings.Disabled)
    report_mock = mocker.patch("ahriman.core.report.report.Report.generate")
    Report.load("x86_64", configuration, "disabled").run(result, [])
    report_mock.assert_called_once_with([], result)


def test_report_console(configuration: Configuration, result: Result, mocker: MockerFixture) -> None:
    """
    must generate console report
    """
    report_mock = mocker.patch("ahriman.core.report.console.Console.generate")
    Report.load("x86_64", configuration, "console").run(result, [])
    report_mock.assert_called_once_with([], result)


def test_report_email(configuration: Configuration, result: Result, mocker: MockerFixture) -> None:
    """
    must generate email report
    """
    report_mock = mocker.patch("ahriman.core.report.email.Email.generate")
    Report.load("x86_64", configuration, "email").run(result, [])
    report_mock.assert_called_once_with([], result)


def test_report_html(configuration: Configuration, result: Result, mocker: MockerFixture) -> None:
    """
    must generate html report
    """
    report_mock = mocker.patch("ahriman.core.report.html.HTML.generate")
    Report.load("x86_64", configuration, "html").run(result, [])
    report_mock.assert_called_once_with([], result)


def test_report_telegram(configuration: Configuration, result: Result, mocker: MockerFixture) -> None:
    """
    must generate telegram report
    """
    report_mock = mocker.patch("ahriman.core.report.telegram.Telegram.generate")
    Report.load("x86_64", configuration, "telegram").run(result, [])
    report_mock.assert_called_once_with([], result)
