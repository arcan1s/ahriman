import pytest

from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.status.watcher import Watcher
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.changes import Changes
from ahriman.models.dependencies import Dependencies
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch


def test_packages(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must return list of available packages
    """
    assert not watcher.packages

    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}
    assert watcher.packages


def test_load(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must correctly load packages
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_get",
                              return_value=[(package_ahriman, BuildStatus())])

    watcher.load()
    cache_mock.assert_called_once_with(None)
    package, status = watcher._known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


def test_load_known(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must correctly load packages with known statuses
    """
    status = BuildStatus(BuildStatusEnum.Success)
    mocker.patch("ahriman.core.status.local_client.LocalClient.package_get", return_value=[(package_ahriman, status)])
    watcher._known = {package_ahriman.base: (package_ahriman, status)}

    watcher.load()
    _, status = watcher._known[package_ahriman.base]
    assert status.status == BuildStatusEnum.Success


def test_package_add(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add package to cache
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_add")

    watcher.package_add(package_ahriman, BuildStatusEnum.Unknown)
    assert watcher.packages
    cache_mock.assert_called_once_with(package_ahriman, pytest.helpers.anyvar(int))


def test_package_changes_get(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must retrieve package changes
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_changes_get")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    watcher.package_changes_get(package_ahriman.base)
    cache_mock.assert_called_once_with(package_ahriman.base)


def test_package_changes_get_failed(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail if package is unknown during fetching changes
    """
    with pytest.raises(UnknownPackageError):
        watcher.package_changes_get(package_ahriman.base)


def test_package_changes_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package changes
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_changes_update")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    watcher.package_changes_update(package_ahriman.base, Changes())
    cache_mock.assert_called_once_with(package_ahriman.base, Changes())


def test_package_changes_update_failed(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail if package is unknown during updating changes
    """
    with pytest.raises(UnknownPackageError):
        watcher.package_changes_update(package_ahriman.base, Changes())


def test_package_dependencies_get(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must retrieve package dependencies
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_dependencies_get")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    watcher.package_dependencies_get(package_ahriman.base)
    cache_mock.assert_called_once_with(package_ahriman.base)


def test_package_dependencies_get_failed(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail if package is unknown during fetching dependencies
    """
    with pytest.raises(UnknownPackageError):
        watcher.package_dependencies_get(package_ahriman.base)


def test_package_dependencies_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package dependencies
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_dependencies_update")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    watcher.package_dependencies_update(package_ahriman.base, Dependencies())
    cache_mock.assert_called_once_with(package_ahriman.base, Dependencies())


def test_package_dependencies_update_failed(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail if package is unknown during updating dependencies
    """
    with pytest.raises(UnknownPackageError):
        watcher.package_dependencies_update(package_ahriman.base, Dependencies())


def test_package_get(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must return package status
    """
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}
    package, status = watcher.package_get(package_ahriman.base)
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


def test_package_get_failed(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail on unknown package
    """
    with pytest.raises(UnknownPackageError):
        watcher.package_get(package_ahriman.base)


def test_package_logs_get(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return package logs
    """
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}
    logs_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_logs_get")

    watcher.package_logs_get(package_ahriman.base, 1, 2)
    logs_mock.assert_called_once_with(package_ahriman.base, 1, 2)


def test_package_logs_get_failed(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must raise UnknownPackageError on logs in case of unknown package
    """
    with pytest.raises(UnknownPackageError):
        watcher.package_logs_get(package_ahriman.base)


def test_package_logs_remove(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package logs
    """
    logs_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_logs_remove")
    watcher.package_logs_remove(package_ahriman.base, "42")
    logs_mock.assert_called_once_with(package_ahriman.base, "42")


def test_package_logs_update_new(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must create package logs record for new package
    """
    delete_mock = mocker.patch("ahriman.core.status.watcher.Watcher.package_logs_remove")
    insert_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_logs_add")

    log_record_id = LogRecordId(package_ahriman.base, watcher._last_log_record_id.version)
    assert watcher._last_log_record_id != log_record_id

    watcher.package_logs_update(log_record_id, 42.01, "log record")
    delete_mock.assert_called_once_with(package_ahriman.base, log_record_id.version)
    insert_mock.assert_called_once_with(log_record_id, 42.01, "log record")

    assert watcher._last_log_record_id == log_record_id


def test_package_logs_update_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must create package logs record for current package
    """
    delete_mock = mocker.patch("ahriman.core.status.watcher.Watcher.package_logs_remove")
    insert_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_logs_add")

    log_record_id = LogRecordId(package_ahriman.base, watcher._last_log_record_id.version)
    watcher._last_log_record_id = log_record_id

    watcher.package_logs_update(log_record_id, 42.01, "log record")
    delete_mock.assert_not_called()
    insert_mock.assert_called_once_with(log_record_id, 42.01, "log record")


def test_package_patches_get(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return patches for the package
    """
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}
    patches_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_patches_get")

    watcher.package_patches_get(package_ahriman.base, None)
    watcher.package_patches_get(package_ahriman.base, "var")
    patches_mock.assert_has_calls([
        MockCall(package_ahriman.base, None),
        MockCall(package_ahriman.base, "var"),
    ])


def test_package_patches_remove(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove patches for the package
    """
    patches_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_patches_remove")
    watcher.package_patches_remove(package_ahriman.base, "var")
    patches_mock.assert_called_once_with(package_ahriman.base, "var")


def test_package_patches_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update patches for the package
    """
    patch = PkgbuildPatch("key", "value")
    patches_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_patches_update")

    watcher.package_patches_update(package_ahriman.base, patch)
    patches_mock.assert_called_once_with(package_ahriman.base, patch)


def test_package_remove(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package base
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_remove")
    logs_mock = mocker.patch("ahriman.core.status.watcher.Watcher.package_logs_remove")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    watcher.package_remove(package_ahriman.base)
    assert not watcher._known
    cache_mock.assert_called_once_with(package_ahriman.base)
    logs_mock.assert_called_once_with(package_ahriman.base, None)


def test_package_remove_unknown(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must not fail on unknown base removal
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_remove")
    watcher.package_remove(package_ahriman.base)
    cache_mock.assert_called_once_with(package_ahriman.base)


def test_package_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package status only for known package
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_update")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    watcher.package_update(package_ahriman.base, BuildStatusEnum.Success)
    cache_mock.assert_called_once_with(package_ahriman.base, pytest.helpers.anyvar(int))
    package, status = watcher._known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Success


def test_package_update_unknown(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail on unknown package status update only
    """
    with pytest.raises(UnknownPackageError):
        watcher.package_update(package_ahriman.base, BuildStatusEnum.Unknown)


def test_status_update(watcher: Watcher) -> None:
    """
    must update service status
    """
    watcher.status_update(BuildStatusEnum.Success)
    assert watcher.status.status == BuildStatusEnum.Success
