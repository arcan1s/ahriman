import pytest

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.status.watcher import Watcher
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package


def test_force_no_report(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> None:
    """
    must force dummy report client
    """
    configuration.set_option("web", "port", "8080")
    load_mock = mocker.patch("ahriman.core.repository.Repository.load")

    Watcher("x86_64", configuration, database)
    load_mock.assert_called_once_with("x86_64", configuration, database, report=False, unsafe=False)


def test_get(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must return package status
    """
    watcher.known = {package_ahriman.base: (package_ahriman, BuildStatus())}
    package, status = watcher.get(package_ahriman.base)
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


def test_get_failed(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail on unknown package
    """
    with pytest.raises(UnknownPackageError):
        watcher.get(package_ahriman.base)


def test_get_logs(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return package logs
    """
    logs_mock = mocker.patch("ahriman.core.database.SQLite.logs_get")
    watcher.get_logs(package_ahriman.base)
    logs_mock.assert_called_once_with(package_ahriman.base)


def test_load(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must correctly load packages
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages", return_value=[package_ahriman])
    cache_mock = mocker.patch("ahriman.core.database.SQLite.packages_get")

    watcher.load()
    cache_mock.assert_called_once_with()
    package, status = watcher.known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


def test_load_known(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must correctly load packages with known statuses
    """
    status = BuildStatus(BuildStatusEnum.Success)
    mocker.patch("ahriman.core.repository.repository.Repository.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.core.database.SQLite.packages_get", return_value=[(package_ahriman, status)])
    watcher.known = {package_ahriman.base: (package_ahriman, status)}

    watcher.load()
    _, status = watcher.known[package_ahriman.base]
    assert status.status == BuildStatusEnum.Success


def test_remove(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package base
    """
    cache_mock = mocker.patch("ahriman.core.database.SQLite.package_remove")
    logs_mock = mocker.patch("ahriman.core.status.watcher.Watcher.remove_logs")
    watcher.known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    watcher.remove(package_ahriman.base)
    assert not watcher.known
    cache_mock.assert_called_once_with(package_ahriman.base)
    logs_mock.assert_called_once_with(package_ahriman.base, None)


def test_remove_logs(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package logs
    """
    logs_mock = mocker.patch("ahriman.core.database.SQLite.logs_remove")
    watcher.remove_logs(package_ahriman.base, 42)
    logs_mock.assert_called_once_with(package_ahriman.base, 42)


def test_remove_unknown(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must not fail on unknown base removal
    """
    cache_mock = mocker.patch("ahriman.core.database.SQLite.package_remove")

    watcher.remove(package_ahriman.base)
    cache_mock.assert_called_once_with(package_ahriman.base)


def test_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package status
    """
    cache_mock = mocker.patch("ahriman.core.database.SQLite.package_update")

    watcher.update(package_ahriman.base, BuildStatusEnum.Unknown, package_ahriman)
    cache_mock.assert_called_once_with(package_ahriman, pytest.helpers.anyvar(int))
    package, status = watcher.known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


def test_update_ping(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package status only for known package
    """
    cache_mock = mocker.patch("ahriman.core.database.SQLite.package_update")
    watcher.known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    watcher.update(package_ahriman.base, BuildStatusEnum.Success, None)
    cache_mock.assert_called_once_with(package_ahriman, pytest.helpers.anyvar(int))
    package, status = watcher.known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Success


def test_update_unknown(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail on unknown package status update only
    """
    with pytest.raises(UnknownPackageError):
        watcher.update(package_ahriman.base, BuildStatusEnum.Unknown, None)


def test_update_logs_new(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must create package logs record for new package
    """
    delete_mock = mocker.patch("ahriman.core.status.watcher.Watcher.remove_logs")
    insert_mock = mocker.patch("ahriman.core.database.SQLite.logs_insert")

    log_record_id = LogRecordId(package_ahriman.base, watcher._last_log_record_id.process_id)
    assert watcher._last_log_record_id != log_record_id

    watcher.update_logs(log_record_id, 42.01, "log record")
    delete_mock.assert_called_once_with(package_ahriman.base, log_record_id.process_id)
    insert_mock.assert_called_once_with(log_record_id, 42.01, "log record")

    assert watcher._last_log_record_id == log_record_id


def test_update_logs_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must create package logs record for current package
    """
    delete_mock = mocker.patch("ahriman.core.status.watcher.Watcher.remove_logs")
    insert_mock = mocker.patch("ahriman.core.database.SQLite.logs_insert")

    log_record_id = LogRecordId(package_ahriman.base, watcher._last_log_record_id.process_id)
    watcher._last_log_record_id = log_record_id

    watcher.update_logs(log_record_id, 42.01, "log record")
    delete_mock.assert_not_called()
    insert_mock.assert_called_once_with(log_record_id, 42.01, "log record")


def test_update_self(watcher: Watcher) -> None:
    """
    must update service status
    """
    watcher.update_self(BuildStatusEnum.Success)
    assert watcher.status.status == BuildStatusEnum.Success
