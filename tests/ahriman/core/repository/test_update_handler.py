import pytest

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.repository.update_handler import UpdateHandler
from ahriman.core.util import utcnow
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.remote_source import RemoteSource


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
    mocker.patch("ahriman.models.package.Package.from_aur", return_value=package_ahriman)
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_pending")

    assert update_handler.updates_aur([], vcs=True) == [package_ahriman]
    status_client_mock.assert_called_once_with(package_ahriman.base)


def test_updates_aur_official(update_handler: UpdateHandler, package_ahriman: Package,
                              mocker: MockerFixture) -> None:
    """
    must provide updates based on repository data
    """
    package_ahriman.remote = RemoteSource.from_source(PackageSource.Repository, package_ahriman.base, "community")
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.models.package.Package.is_outdated", return_value=True)
    mocker.patch("ahriman.models.package.Package.from_official", return_value=package_ahriman)
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_pending")

    assert update_handler.updates_aur([], vcs=True) == [package_ahriman]
    status_client_mock.assert_called_once_with(package_ahriman.base)


def test_updates_aur_failed(update_handler: UpdateHandler, package_ahriman: Package,
                            mocker: MockerFixture) -> None:
    """
    must update status via client for failed load
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.models.package.Package.from_aur", side_effect=Exception())
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_failed")

    update_handler.updates_aur([], vcs=True)
    status_client_mock.assert_called_once_with(package_ahriman.base)


def test_updates_aur_filter(update_handler: UpdateHandler, package_ahriman: Package, package_python_schedule: Package,
                            mocker: MockerFixture) -> None:
    """
    must provide updates only for filtered packages
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages",
                 return_value=[package_ahriman, package_python_schedule])
    mocker.patch("ahriman.models.package.Package.is_outdated", return_value=True)
    package_load_mock = mocker.patch("ahriman.models.package.Package.from_aur", return_value=package_ahriman)

    assert update_handler.updates_aur([package_ahriman.base], vcs=True) == [package_ahriman]
    package_load_mock.assert_called_once_with(package_ahriman.base, update_handler.pacman)


def test_updates_aur_ignore(update_handler: UpdateHandler, package_ahriman: Package,
                            mocker: MockerFixture) -> None:
    """
    must skip ignore packages
    """
    update_handler.ignore_list = [package_ahriman.base]
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    package_load_mock = mocker.patch("ahriman.models.package.Package.from_aur")

    assert not update_handler.updates_aur([], vcs=True)
    package_load_mock.assert_not_called()


def test_updates_aur_ignore_vcs(update_handler: UpdateHandler, package_ahriman: Package,
                                mocker: MockerFixture) -> None:
    """
    must skip VCS packages check if requested
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.models.package.Package.from_aur", return_value=package_ahriman)
    mocker.patch("ahriman.models.package.Package.is_vcs", return_value=True)
    package_is_newer_than_mock = mocker.patch("ahriman.models.package.Package.is_newer_than", return_value=True)
    package_is_outdated_mock = mocker.patch("ahriman.models.package.Package.is_outdated", return_value=False)
    ts1 = utcnow().timestamp()

    assert not update_handler.updates_aur([], vcs=False)
    package_is_newer_than_mock.assert_called_once_with(pytest.helpers.anyvar(float, strict=True))
    assert ts1 < package_is_newer_than_mock.call_args[0][0] < utcnow().timestamp()
    package_is_outdated_mock.assert_called_once_with(package_ahriman, update_handler.paths, calculate_version=False)


def test_updates_local(update_handler: UpdateHandler, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must check for updates for locally stored packages
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    mocker.patch("pathlib.Path.iterdir", return_value=[Path(package_ahriman.base)])
    mocker.patch("ahriman.models.package.Package.is_outdated", return_value=True)
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    package_load_mock = mocker.patch("ahriman.models.package.Package.from_build", return_value=package_ahriman)
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_pending")

    assert update_handler.updates_local() == [package_ahriman]
    fetch_mock.assert_called_once_with(Path(package_ahriman.base), remote=None)
    package_load_mock.assert_called_once_with(Path(package_ahriman.base))
    status_client_mock.assert_called_once_with(package_ahriman.base)


def test_updates_local_unknown(update_handler: UpdateHandler, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return unknown package as out-dated
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[])
    mocker.patch("pathlib.Path.iterdir", return_value=[Path(package_ahriman.base)])
    mocker.patch("ahriman.models.package.Package.is_outdated", return_value=True)
    mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    mocker.patch("ahriman.models.package.Package.from_build", return_value=package_ahriman)
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_unknown")

    assert update_handler.updates_local() == [package_ahriman]
    status_client_mock.assert_called_once_with(package_ahriman)


def test_updates_local_with_failures(update_handler: UpdateHandler, package_ahriman: Package,
                                     mocker: MockerFixture) -> None:
    """
    must process local through the packages with failure
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages")
    mocker.patch("pathlib.Path.iterdir", return_value=[Path(package_ahriman.base)])
    mocker.patch("ahriman.core.build_tools.sources.Sources.fetch", side_effect=Exception())

    assert not update_handler.updates_local()


def test_updates_manual_clear(update_handler: UpdateHandler, mocker: MockerFixture) -> None:
    """
    requesting manual updates must clear packages directory
    """
    mocker.patch("pathlib.Path.iterdir", return_value=[])
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages")

    update_handler.updates_manual()

    from ahriman.core.repository.cleaner import Cleaner
    Cleaner.clear_queue.assert_called_once_with()


def test_updates_manual_status_known(update_handler: UpdateHandler, package_ahriman: Package,
                                     mocker: MockerFixture) -> None:
    """
    must create record for known package via reporter
    """
    mocker.patch("ahriman.core.database.SQLite.build_queue_get", return_value=[package_ahriman])
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_pending")

    update_handler.updates_manual()
    status_client_mock.assert_called_once_with(package_ahriman.base)


def test_updates_manual_status_unknown(update_handler: UpdateHandler, package_ahriman: Package,
                                       mocker: MockerFixture) -> None:
    """
    must create record for unknown package via reporter
    """
    mocker.patch("ahriman.core.database.SQLite.build_queue_get", return_value=[package_ahriman])
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[])
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_unknown")

    update_handler.updates_manual()
    status_client_mock.assert_called_once_with(package_ahriman)


def test_updates_manual_with_failures(update_handler: UpdateHandler, package_ahriman: Package,
                                      mocker: MockerFixture) -> None:
    """
    must process manual through the packages with failure
    """
    mocker.patch("ahriman.core.database.SQLite.build_queue_get", side_effect=Exception())
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    assert update_handler.updates_manual() == []
