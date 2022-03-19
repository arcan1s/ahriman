from pytest_mock import MockerFixture

from ahriman.application.application import Application
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_finalize(application: Application, mocker: MockerFixture) -> None:
    """
    must report and sync at the last
    """
    report_mock = mocker.patch("ahriman.application.application.Application.report")
    sync_mock = mocker.patch("ahriman.application.application.Application.sync")

    application._finalize(Result())
    report_mock.assert_called_once_with([], Result())
    sync_mock.assert_called_once_with([], [])


def test_known_packages(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return not empty list of known packages
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages", return_value=[package_ahriman])
    packages = application._known_packages()
    assert len(packages) > 1
    assert package_ahriman.base in packages
