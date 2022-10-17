from pytest_mock import MockerFixture

from ahriman.application.application import Application
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_known_packages(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return not empty list of known packages
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages", return_value=[package_ahriman])
    packages = application._known_packages()
    assert len(packages) > 1
    assert package_ahriman.base in packages


def test_on_result(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must call on_result trigger function
    """
    mocker.patch("ahriman.core.repository.Repository.packages", return_value=[package_ahriman])
    triggers_mock = mocker.patch("ahriman.core.triggers.TriggerLoader.on_result")

    application.on_result(Result())
    triggers_mock.assert_called_once_with(Result(), [package_ahriman])


def test_on_start(application: Application, mocker: MockerFixture) -> None:
    """
    must call on_start trigger function
    """
    triggers_mock = mocker.patch("ahriman.core.triggers.TriggerLoader.on_start")

    application.on_start()
    triggers_mock.assert_called_once_with()


def test_on_stop(application: Application, mocker: MockerFixture) -> None:
    """
    must call on_stop trigger function
    """
    triggers_mock = mocker.patch("ahriman.core.triggers.TriggerLoader.on_stop")

    application.on_stop()
    triggers_mock.assert_called_once_with()
