import pytest

from pytest_mock import MockerFixture

from ahriman.core.repository.update_handler import UpdateHandler
from ahriman.models.package import Package


def test_packages(update_handler: UpdateHandler) -> None:
    """
    must raise NotImplemented for missing method
    """
    with pytest.raises(NotImplementedError):
        update_handler.packages()


def test_updates_aur(update_handler: UpdateHandler, package_ahriman: Package,
                     mocker: MockerFixture) -> None:
    """
    must provide updates with status updates
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.models.package.Package.is_outdated", return_value=True)
    mocker.patch("ahriman.models.package.Package.load", return_value=package_ahriman)
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_pending")

    assert update_handler.updates_aur([], False) == [package_ahriman]
    status_client_mock.assert_called_once()


def test_updates_aur_failed(update_handler: UpdateHandler, package_ahriman: Package,
                            mocker: MockerFixture) -> None:
    """
    must update status via client for failed load
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.models.package.Package.load", side_effect=Exception())
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_failed")

    update_handler.updates_aur([], False)
    status_client_mock.assert_called_once()


def test_updates_aur_filter(update_handler: UpdateHandler, package_ahriman: Package, package_python_schedule: Package,
                            mocker: MockerFixture) -> None:
    """
    must provide updates only for filtered packages
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages",
                 return_value=[package_ahriman, package_python_schedule])
    mocker.patch("ahriman.models.package.Package.is_outdated", return_value=True)
    package_load_mock = mocker.patch("ahriman.models.package.Package.load", return_value=package_ahriman)

    assert update_handler.updates_aur([package_ahriman.base], False) == [package_ahriman]
    package_load_mock.assert_called_once()


def test_updates_aur_ignore(update_handler: UpdateHandler, package_ahriman: Package,
                            mocker: MockerFixture) -> None:
    """
    must skip ignore packages
    """
    update_handler.ignore_list = [package_ahriman.base]
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    package_load_mock = mocker.patch("ahriman.models.package.Package.load")

    update_handler.updates_aur([], False)
    package_load_mock.assert_not_called()


def test_updates_aur_ignore_vcs(update_handler: UpdateHandler, package_ahriman: Package,
                                mocker: MockerFixture) -> None:
    """
    must skip VCS packages check if requested
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.models.package.Package.is_vcs", return_value=True)
    package_is_outdated_mock = mocker.patch("ahriman.models.package.Package.is_outdated")

    update_handler.updates_aur([], True)
    package_is_outdated_mock.assert_not_called()


def test_updates_manual_clear(update_handler: UpdateHandler, mocker: MockerFixture) -> None:
    """
    requesting manual updates must clear packages directory
    """
    mocker.patch("pathlib.Path.iterdir", return_value=[])
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages")

    update_handler.updates_manual()

    from ahriman.core.repository.cleaner import Cleaner
    Cleaner.clear_manual.assert_called_once()


def test_updates_manual_status_known(update_handler: UpdateHandler, package_ahriman: Package,
                                     mocker: MockerFixture) -> None:
    """
    must create record for known package via reporter
    """
    mocker.patch("pathlib.Path.iterdir", return_value=[package_ahriman.base])
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.models.package.Package.load", return_value=package_ahriman)
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_pending")

    update_handler.updates_manual()
    status_client_mock.assert_called_once()


def test_updates_manual_status_unknown(update_handler: UpdateHandler, package_ahriman: Package,
                                       mocker: MockerFixture) -> None:
    """
    must create record for unknown package via reporter
    """
    mocker.patch("pathlib.Path.iterdir", return_value=[package_ahriman.base])
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[])
    mocker.patch("ahriman.models.package.Package.load", return_value=package_ahriman)
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_unknown")

    update_handler.updates_manual()
    status_client_mock.assert_called_once()


def test_updates_manual_with_failures(update_handler: UpdateHandler, package_ahriman: Package,
                                      mocker: MockerFixture) -> None:
    """
    must process through the packages with failure
    """
    mocker.patch("pathlib.Path.iterdir", return_value=[package_ahriman.base])
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[])
    mocker.patch("ahriman.models.package.Package.load", side_effect=Exception())

    assert update_handler.updates_manual() == []
