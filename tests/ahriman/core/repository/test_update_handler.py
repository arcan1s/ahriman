import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any

from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.repository.update_handler import UpdateHandler
from ahriman.models.dependencies import Dependencies
from ahriman.models.event import EventType
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.remote_source import RemoteSource


def test_updates_aur(update_handler: UpdateHandler, package_ahriman: Package,
                     mocker: MockerFixture) -> None:
    """
    must provide updates with status updates
    """
    packages_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages",
                                 return_value=[package_ahriman])
    mocker.patch("ahriman.models.package.Package.from_aur", return_value=package_ahriman)
    status_client_mock = mocker.patch("ahriman.core.status.Client.set_pending")
    event_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.event")
    package_is_outdated_mock = mocker.patch("ahriman.models.package.Package.is_outdated", return_value=True)

    assert update_handler.updates_aur([], vcs=True) == [package_ahriman]
    packages_mock.assert_called_once_with([])
    status_client_mock.assert_called_once_with(package_ahriman.base)
    event_mock.assert_called_once_with(package_ahriman.base, EventType.PackageOutdated,
                                       pytest.helpers.anyvar(str, True))
    package_is_outdated_mock.assert_called_once_with(
        package_ahriman, update_handler.paths,
        vcs_allowed_age=update_handler.vcs_allowed_age,
        calculate_version=True)


def test_updates_aur_official(update_handler: UpdateHandler, package_ahriman: Package,
                              mocker: MockerFixture) -> None:
    """
    must provide updates based on repository data
    """
    package_ahriman.remote = RemoteSource(source=PackageSource.Repository)
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.models.package.Package.is_outdated", return_value=True)
    mocker.patch("ahriman.models.package.Package.from_official", return_value=package_ahriman)
    status_client_mock = mocker.patch("ahriman.core.status.Client.set_pending")
    event_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.event")

    assert update_handler.updates_aur([], vcs=True) == [package_ahriman]
    status_client_mock.assert_called_once_with(package_ahriman.base)
    event_mock.assert_called_once_with(package_ahriman.base, EventType.PackageOutdated,
                                       pytest.helpers.anyvar(str, True))


def test_updates_aur_failed(update_handler: UpdateHandler, package_ahriman: Package,
                            mocker: MockerFixture) -> None:
    """
    must update status via client for failed load
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.models.package.Package.from_aur", side_effect=Exception())
    status_client_mock = mocker.patch("ahriman.core.status.Client.set_failed")

    update_handler.updates_aur([], vcs=True)
    status_client_mock.assert_called_once_with(package_ahriman.base)


def test_updates_aur_local(update_handler: UpdateHandler, package_ahriman: Package,
                           mocker: MockerFixture) -> None:
    """
    must skip packages with local sources
    """
    package_ahriman.remote = RemoteSource(source=PackageSource.Local)
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    package_load_mock = mocker.patch("ahriman.models.package.Package.from_aur")

    assert not update_handler.updates_aur([], vcs=True)
    package_load_mock.assert_not_called()


def test_updates_aur_filter(update_handler: UpdateHandler, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must provide updates only for filtered packages
    """
    packages_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages",
                                 return_value=[package_ahriman])
    mocker.patch("ahriman.models.package.Package.is_outdated", return_value=True)
    package_load_mock = mocker.patch("ahriman.models.package.Package.from_aur", return_value=package_ahriman)

    assert update_handler.updates_aur([package_ahriman.base], vcs=True) == [package_ahriman]
    packages_mock.assert_called_once_with([package_ahriman.base])
    package_load_mock.assert_called_once_with(package_ahriman.base, None)


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
    package_is_outdated_mock = mocker.patch("ahriman.models.package.Package.is_outdated", return_value=False)

    assert not update_handler.updates_aur([], vcs=False)
    package_is_outdated_mock.assert_called_once_with(
        package_ahriman, update_handler.paths,
        vcs_allowed_age=update_handler.vcs_allowed_age,
        calculate_version=False)


def test_updates_aur_load_by_package(update_handler: UpdateHandler, package_python_schedule: Package,
                                     mocker: MockerFixture) -> None:
    """
    must load package by package name if none found by base
    """
    def package_selector(name: str, *_: Any) -> Package:
        if name == package_python_schedule.base:
            raise UnknownPackageError(name)
        return package_python_schedule

    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages",
                 return_value=[package_python_schedule])
    mocker.patch("ahriman.models.package.Package.from_aur", side_effect=package_selector)
    mocker.patch("ahriman.models.package.Package.is_outdated", return_value=True)
    assert update_handler.updates_aur([], vcs=True) == [package_python_schedule]


def test_updates_aur_load_by_package_failed(update_handler: UpdateHandler, package_ahriman: Package,
                                            mocker: MockerFixture) -> None:
    """
    must update status via client for failed load
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.models.package.Package.from_aur", side_effect=UnknownPackageError(package_ahriman.base))
    mocker.patch("ahriman.core.status.Client.set_failed")

    update_handler.updates_aur([], vcs=True)


def test_updates_dependencies(update_handler: UpdateHandler, package_ahriman: Package, package_python_schedule: Package,
                              mocker: MockerFixture) -> None:
    """
    must define updates with broken dependencies
    """
    packages_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages",
                                 return_value=[package_ahriman, package_python_schedule])
    status_client_mock = mocker.patch("ahriman.core.status.Client.set_pending")
    event_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.event")
    dependencies = {
        package_ahriman.base: Dependencies({"usr/lib/python3.11/site-packages": ["python"]}),
        package_python_schedule.base: Dependencies({"usr/lib/python3.12/site-packages": ["python"]}),
    }
    mocker.patch("ahriman.core.status.local_client.LocalClient.package_dependencies_get",
                 side_effect=lambda base: dependencies[base])
    mocker.patch("ahriman.core.alpm.pacman.Pacman.files",
                 return_value={"python": {"usr/lib/python3.12/site-packages"}})

    assert update_handler.updates_dependencies(["filter"]) == [package_ahriman]
    packages_mock.assert_called_once_with(["filter"])
    status_client_mock.assert_called_once_with(package_ahriman.base)
    event_mock.assert_called_once_with(package_ahriman.base, EventType.PackageOutdated,
                                       pytest.helpers.anyvar(str, True))


def test_updates_dependencies_skip_unknown(update_handler: UpdateHandler, package_ahriman: Package,
                                           mocker: MockerFixture) -> None:
    """
    must skip unknown package dependencies
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.core.status.local_client.LocalClient.package_dependencies_get",
                 return_value=Dependencies())
    mocker.patch("ahriman.core.alpm.pacman.Pacman.files",
                 return_value={"python": {"usr/lib/python3.12/site-packages"}})

    assert update_handler.updates_dependencies(["filter"]) == []


def test_updates_dependencies_partial(update_handler: UpdateHandler, package_ahriman: Package,
                                      mocker: MockerFixture) -> None:
    """
    must skip broken dependencies update if at least one package provides file
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    dependencies = Dependencies({"usr": ["filesystem", "python"]})
    mocker.patch("ahriman.core.status.local_client.LocalClient.package_dependencies_get", return_value=dependencies)
    mocker.patch("ahriman.core.alpm.pacman.Pacman.files", return_value={
        "filesystem": {"usr"},
        "python": {"usr"},
    })

    assert update_handler.updates_dependencies(["filter"]) == []


def test_updates_local(update_handler: UpdateHandler, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must check for updates for locally stored packages
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    mocker.patch("pathlib.Path.iterdir", return_value=[Path(package_ahriman.base)])
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    package_load_mock = mocker.patch("ahriman.models.package.Package.from_build", return_value=package_ahriman)
    status_client_mock = mocker.patch("ahriman.core.status.Client.set_pending")
    event_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.event")
    package_is_outdated_mock = mocker.patch("ahriman.models.package.Package.is_outdated", return_value=True)

    assert update_handler.updates_local(vcs=True) == [package_ahriman]
    fetch_mock.assert_called_once_with(Path(package_ahriman.base), pytest.helpers.anyvar(int))
    package_load_mock.assert_called_once_with(Path(package_ahriman.base), "x86_64", None)
    status_client_mock.assert_called_once_with(package_ahriman.base)
    event_mock.assert_called_once_with(package_ahriman.base, EventType.PackageOutdated,
                                       pytest.helpers.anyvar(str, True))
    package_is_outdated_mock.assert_called_once_with(
        package_ahriman, update_handler.paths,
        vcs_allowed_age=update_handler.vcs_allowed_age,
        calculate_version=True)


def test_updates_local_ignore_vcs(update_handler: UpdateHandler, package_ahriman: Package,
                                  mocker: MockerFixture) -> None:
    """
    must skip VCS packages check if requested for locally stored packages
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    mocker.patch("pathlib.Path.iterdir", return_value=[Path(package_ahriman.base)])
    mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    mocker.patch("ahriman.models.package.Package.from_build", return_value=package_ahriman)
    package_is_outdated_mock = mocker.patch("ahriman.models.package.Package.is_outdated", return_value=False)

    assert not update_handler.updates_local(vcs=False)
    package_is_outdated_mock.assert_called_once_with(
        package_ahriman, update_handler.paths,
        vcs_allowed_age=update_handler.vcs_allowed_age,
        calculate_version=False)


def test_updates_local_unknown(update_handler: UpdateHandler, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return unknown package as out-dated
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[])
    mocker.patch("pathlib.Path.iterdir", return_value=[Path(package_ahriman.base)])
    mocker.patch("ahriman.models.package.Package.is_outdated", return_value=True)
    mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    mocker.patch("ahriman.models.package.Package.from_build", return_value=package_ahriman)

    assert update_handler.updates_local(vcs=True) == []


def test_updates_local_with_failures(update_handler: UpdateHandler, package_ahriman: Package,
                                     mocker: MockerFixture) -> None:
    """
    must process local through the packages with failure
    """
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages")
    mocker.patch("pathlib.Path.iterdir", return_value=[Path(package_ahriman.base)])
    mocker.patch("ahriman.core.build_tools.sources.Sources.fetch", side_effect=Exception())

    assert not update_handler.updates_local(vcs=True)


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
    status_client_mock = mocker.patch("ahriman.core.status.Client.set_pending")
    event_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.event")

    update_handler.updates_manual()
    status_client_mock.assert_called_once_with(package_ahriman.base)
    event_mock.assert_called_once_with(package_ahriman.base, EventType.PackageOutdated,
                                       pytest.helpers.anyvar(str, True))


def test_updates_manual_status_unknown(update_handler: UpdateHandler, package_ahriman: Package,
                                       mocker: MockerFixture) -> None:
    """
    must create record for unknown package via reporter
    """
    mocker.patch("ahriman.core.database.SQLite.build_queue_get", return_value=[package_ahriman])
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[])
    status_client_mock = mocker.patch("ahriman.core.status.Client.set_unknown")
    event_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.event")

    update_handler.updates_manual()
    status_client_mock.assert_called_once_with(package_ahriman)
    event_mock.assert_called_once_with(package_ahriman.base, EventType.PackageOutdated,
                                       pytest.helpers.anyvar(str, True))


def test_updates_manual_with_failures(update_handler: UpdateHandler, package_ahriman: Package,
                                      mocker: MockerFixture) -> None:
    """
    must process manual through the packages with failure
    """
    mocker.patch("ahriman.core.database.SQLite.build_queue_get", side_effect=Exception())
    mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.packages", return_value=[package_ahriman])
    assert update_handler.updates_manual() == []
