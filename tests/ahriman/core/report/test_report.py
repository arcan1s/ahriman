import pytest

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import ReportFailed
from ahriman.core.report.report import Report
from ahriman.models.report_settings import ReportSettings


def test_report_failure(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must raise ReportFailed on errors
    """
    mocker.patch("ahriman.core.report.html.HTML.generate", side_effect=Exception())
    with pytest.raises(ReportFailed):
        Report.run("x86_64", configuration, ReportSettings.HTML.name, Path("path"))


def test_report_html(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must generate html report
    """
    report_mock = mocker.patch("ahriman.core.report.html.HTML.generate")
    Report.run("x86_64", configuration, ReportSettings.HTML.name, Path("path"))
    report_mock.assert_called_once()
