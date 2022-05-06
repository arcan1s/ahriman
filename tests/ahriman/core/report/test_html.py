import pytest

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.report import HTML
from ahriman.models.package import Package


def test_generate(configuration: Configuration, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must generate report
    """
    write_mock = mocker.patch("pathlib.Path.write_text")

    report = HTML("x86_64", configuration, "html")
    report.generate([package_ahriman], [])
    write_mock.assert_called_once_with(pytest.helpers.anyvar(int))
