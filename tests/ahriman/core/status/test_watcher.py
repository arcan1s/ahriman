import pytest

from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.status.watcher import Watcher
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.changes import Changes
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.worker import Worker


def test_load(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must correctly load packages
    """
    cache_mock = mocker.patch("ahriman.core.database.SQLite.packages_get",
                              return_value=[(package_ahriman, BuildStatus())])

    watcher.load()
    cache_mock.assert_called_once_with(watcher.repository_id)
    package, status = watcher.known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


def test_load_known(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must correctly load packages with known statuses
    """
    status = BuildStatus(BuildStatusEnum.Success)
    mocker.patch("ahriman.core.database.SQLite.packages_get", return_value=[(package_ahriman, status)])
    watcher.known = {package_ahriman.base: (package_ahriman, status)}

    watcher.load()
    _, status = watcher.known[package_ahriman.base]
    assert status.status == BuildStatusEnum.Success


def test_logs_get(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return package logs
    """
    logs_mock = mocker.patch("ahriman.core.database.SQLite.logs_get")
    watcher.logs_get(package_ahriman.base, 1, 2)
    logs_mock.assert_called_once_with(package_ahriman.base, 1, 2, watcher.repository_id)


def test_logs_remove(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package logs
    """
    logs_mock = mocker.patch("ahriman.core.database.SQLite.logs_remove")
    watcher.logs_remove(package_ahriman.base, "42")
    logs_mock.assert_called_once_with(package_ahriman.base, "42", watcher.repository_id)


def test_logs_update_new(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must create package logs record for new package
    """
    delete_mock = mocker.patch("ahriman.core.status.watcher.Watcher.logs_remove")
    insert_mock = mocker.patch("ahriman.core.database.SQLite.logs_insert")

    log_record_id = LogRecordId(package_ahriman.base, watcher._last_log_record_id.version)
    assert watcher._last_log_record_id != log_record_id

    watcher.logs_update(log_record_id, 42.01, "log record")
    delete_mock.assert_called_once_with(package_ahriman.base, log_record_id.version)
    insert_mock.assert_called_once_with(log_record_id, 42.01, "log record", watcher.repository_id)

    assert watcher._last_log_record_id == log_record_id


def test_logs_update_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must create package logs record for current package
    """
    delete_mock = mocker.patch("ahriman.core.status.watcher.Watcher.logs_remove")
    insert_mock = mocker.patch("ahriman.core.database.SQLite.logs_insert")

    log_record_id = LogRecordId(package_ahriman.base, watcher._last_log_record_id.version)
    watcher._last_log_record_id = log_record_id

    watcher.logs_update(log_record_id, 42.01, "log record")
    delete_mock.assert_not_called()
    insert_mock.assert_called_once_with(log_record_id, 42.01, "log record", watcher.repository_id)


def test_package_changes_get(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return package changes
    """
    get_mock = mocker.patch("ahriman.core.database.SQLite.changes_get", return_value=Changes("sha"))
    watcher.known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    assert watcher.package_changes_get(package_ahriman.base) == Changes("sha")
    get_mock.assert_called_once_with(package_ahriman.base, watcher.repository_id)


def test_package_changes_get_failed(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must raise UnknownPackageError in case of unknown package
    """
    with pytest.raises(UnknownPackageError):
        watcher.package_changes_get(package_ahriman.base)


def test_package_get(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must return package status
    """
    watcher.known = {package_ahriman.base: (package_ahriman, BuildStatus())}
    package, status = watcher.package_get(package_ahriman.base)
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


def test_package_get_failed(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail on unknown package
    """
    with pytest.raises(UnknownPackageError):
        watcher.package_get(package_ahriman.base)


def test_package_remove(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package base
    """
    cache_mock = mocker.patch("ahriman.core.database.SQLite.package_remove")
    logs_mock = mocker.patch("ahriman.core.status.watcher.Watcher.logs_remove")
    watcher.known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    watcher.package_remove(package_ahriman.base)
    assert not watcher.known
    cache_mock.assert_called_once_with(package_ahriman.base, watcher.repository_id)
    logs_mock.assert_called_once_with(package_ahriman.base, None)


def test_package_remove_unknown(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must not fail on unknown base removal
    """
    cache_mock = mocker.patch("ahriman.core.database.SQLite.package_remove")

    watcher.package_remove(package_ahriman.base)
    cache_mock.assert_called_once_with(package_ahriman.base, watcher.repository_id)


def test_package_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package status
    """
    cache_mock = mocker.patch("ahriman.core.database.SQLite.package_update")

    watcher.package_update(package_ahriman.base, BuildStatusEnum.Unknown, package_ahriman)
    cache_mock.assert_called_once_with(package_ahriman, pytest.helpers.anyvar(int), watcher.repository_id)
    package, status = watcher.known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


def test_package_update_ping(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package status only for known package
    """
    cache_mock = mocker.patch("ahriman.core.database.SQLite.package_update")
    watcher.known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    watcher.package_update(package_ahriman.base, BuildStatusEnum.Success, None)
    cache_mock.assert_called_once_with(package_ahriman, pytest.helpers.anyvar(int), watcher.repository_id)
    package, status = watcher.known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Success


def test_package_update_unknown(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail on unknown package status update only
    """
    with pytest.raises(UnknownPackageError):
        watcher.package_update(package_ahriman.base, BuildStatusEnum.Unknown, None)


def test_patches_get(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return patches for the package
    """
    patches_mock = mocker.patch("ahriman.core.database.SQLite.patches_list")

    watcher.patches_get(package_ahriman.base, None)
    watcher.patches_get(package_ahriman.base, "var")
    patches_mock.assert_has_calls([
        MockCall(package_ahriman.base, None),
        MockCall().get(package_ahriman.base, []),
        MockCall(package_ahriman.base, ["var"]),
        MockCall().get(package_ahriman.base, []),
    ])


def test_patches_remove(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove patches for the package
    """
    patches_mock = mocker.patch("ahriman.core.database.SQLite.patches_remove")
    watcher.patches_remove(package_ahriman.base, "var")
    patches_mock.assert_called_once_with(package_ahriman.base, ["var"])


def test_patches_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update patches for the package
    """
    patch = PkgbuildPatch("key", "value")
    patches_mock = mocker.patch("ahriman.core.database.SQLite.patches_insert")

    watcher.patches_update(package_ahriman.base, patch)
    patches_mock.assert_called_once_with(package_ahriman.base, [patch])


def test_status_update(watcher: Watcher) -> None:
    """
    must update service status
    """
    watcher.status_update(BuildStatusEnum.Success)
    assert watcher.status.status == BuildStatusEnum.Success


def test_workers_get(watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must retrieve workers
    """
    worker = Worker("remote")
    worker_mock = mocker.patch("ahriman.core.database.SQLite.workers_get", return_value=[worker])

    assert watcher.workers_get() == [worker]
    worker_mock.assert_called_once_with()


def test_workers_remove(watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must remove workers
    """
    identifier = "identifier"
    worker_mock = mocker.patch("ahriman.core.database.SQLite.workers_remove")

    watcher.workers_remove(identifier)
    watcher.workers_remove()
    worker_mock.assert_has_calls([
        MockCall(identifier),
        MockCall(None),
    ])


def test_workers_update(watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must update workers
    """
    worker = Worker("remote")
    worker_mock = mocker.patch("ahriman.core.database.SQLite.workers_insert")

    watcher.workers_update(worker)
    worker_mock.assert_called_once_with(worker)
