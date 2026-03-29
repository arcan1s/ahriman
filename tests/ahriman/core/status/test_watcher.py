import pytest

from pytest_mock import MockerFixture

from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.status.watcher import Watcher
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.changes import Changes
from ahriman.models.dependencies import Dependencies
from ahriman.models.event import Event, EventType
from ahriman.models.log_record import LogRecord
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch


async def test_event_add(watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must create new event
    """
    event = Event("event", "object")
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.event_add")

    await watcher.event_add(event)
    cache_mock.assert_called_once_with(event)


async def test_event_get(watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must retrieve events
    """
    event = Event("event", "object")
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.event_get", return_value=[event])

    result = await watcher.event_get(None, None)
    assert result == [event]
    cache_mock.assert_called_once_with(None, None, None, None, -1, 0)


async def test_load(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must correctly load packages
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_get",
                              return_value=[(package_ahriman, BuildStatus())])

    await watcher.load()
    cache_mock.assert_called_once_with(None)
    package, status = watcher._known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


async def test_load_known(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must correctly load packages with known statuses
    """
    status = BuildStatus(BuildStatusEnum.Success)
    mocker.patch("ahriman.core.status.local_client.LocalClient.package_get", return_value=[(package_ahriman, status)])
    watcher._known = {package_ahriman.base: (package_ahriman, status)}

    await watcher.load()
    _, status = watcher._known[package_ahriman.base]
    assert status.status == BuildStatusEnum.Success


async def test_logs_rotate(watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must rotate logs
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.logs_rotate")
    await watcher.logs_rotate(42)
    cache_mock.assert_called_once_with(42)


async def test_package_archives(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return package archives from package info
    """
    archives_mock = mocker.patch("ahriman.core.repository.package_info.PackageInfo.package_archives",
                                 return_value=[package_ahriman])

    result = await watcher.package_archives(package_ahriman.base)
    assert result == [package_ahriman]
    archives_mock.assert_called_once_with(package_ahriman.base)


async def test_package_get(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must return package status
    """
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}
    package, status = await watcher.package_get(package_ahriman.base)
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


async def test_package_get_failed(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail on unknown package
    """
    with pytest.raises(UnknownPackageError):
        await watcher.package_get(package_ahriman.base)


async def test_package_changes_get(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return package changes
    """
    changes = Changes("sha")
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_changes_get",
                              return_value=changes)

    assert await watcher.package_changes_get(package_ahriman.base) == changes
    cache_mock.assert_called_once_with(package_ahriman.base)


async def test_package_changes_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package changes
    """
    changes = Changes("sha")
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_changes_update")

    await watcher.package_changes_update(package_ahriman.base, changes)
    cache_mock.assert_called_once_with(package_ahriman.base, changes)


async def test_package_dependencies_get(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return package dependencies
    """
    dependencies = Dependencies({"path": [package_ahriman.base]})
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_dependencies_get",
                              return_value=dependencies)

    assert await watcher.package_dependencies_get(package_ahriman.base) == dependencies
    cache_mock.assert_called_once_with(package_ahriman.base)


async def test_package_dependencies_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package dependencies
    """
    dependencies = Dependencies({"path": [package_ahriman.base]})
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_dependencies_update")

    await watcher.package_dependencies_update(package_ahriman.base, dependencies)
    cache_mock.assert_called_once_with(package_ahriman.base, dependencies)


async def test_package_hold_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package hold status
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_hold_update")
    broadcast_mock = mocker.patch("ahriman.core.status.event_bus.EventBus.broadcast")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    await watcher.package_hold_update(package_ahriman.base, enabled=True)
    cache_mock.assert_called_once_with(package_ahriman.base, enabled=True)
    _, status = watcher._known[package_ahriman.base]
    assert status.is_held is True
    broadcast_mock.assert_called_once_with(EventType.PackageHeld, package_ahriman.base, is_held=True)


async def test_package_hold_update_unknown(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail on unknown package hold update
    """
    with pytest.raises(UnknownPackageError):
        await watcher.package_hold_update(package_ahriman.base, enabled=True)


async def test_package_logs_add(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must post log record
    """
    log_record = LogRecord(LogRecordId(package_ahriman.base, "1.0.0"), 42.0, "message")
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_logs_add")
    broadcast_mock = mocker.patch("ahriman.core.status.event_bus.EventBus.broadcast")

    await watcher.package_logs_add(log_record)
    cache_mock.assert_called_once_with(log_record)
    broadcast_mock.assert_called_once_with(EventType.BuildLog, package_ahriman.base, **log_record.view())


async def test_package_logs_get(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return package logs
    """
    log_record = LogRecord(LogRecordId(package_ahriman.base, "1.0.0"), 42.0, "message")
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_logs_get",
                              return_value=[log_record])

    assert await watcher.package_logs_get(package_ahriman.base) == [log_record]
    cache_mock.assert_called_once_with(package_ahriman.base, None, None, -1, 0)


async def test_package_logs_remove(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package logs
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_logs_remove")
    await watcher.package_logs_remove(package_ahriman.base, None)
    cache_mock.assert_called_once_with(package_ahriman.base, None)


async def test_package_patches_get(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return package patches
    """
    patch = PkgbuildPatch("key", "value")
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_patches_get", return_value=[patch])

    assert await watcher.package_patches_get(package_ahriman.base, None) == [patch]
    cache_mock.assert_called_once_with(package_ahriman.base, None)


async def test_package_patches_remove(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package patches
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_patches_remove")
    await watcher.package_patches_remove(package_ahriman.base, None)
    cache_mock.assert_called_once_with(package_ahriman.base, None)


async def test_package_patches_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package patches
    """
    patch = PkgbuildPatch("key", "value")
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_patches_update")

    await watcher.package_patches_update(package_ahriman.base, patch)
    cache_mock.assert_called_once_with(package_ahriman.base, patch)


async def test_package_remove(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package base
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_remove")
    broadcast_mock = mocker.patch("ahriman.core.status.event_bus.EventBus.broadcast")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    await watcher.package_remove(package_ahriman.base)
    assert not watcher._known
    cache_mock.assert_called_once_with(package_ahriman.base)
    broadcast_mock.assert_called_once_with(EventType.PackageRemoved, package_ahriman.base)


async def test_package_remove_unknown(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must not fail on unknown base removal
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_remove")
    broadcast_mock = mocker.patch("ahriman.core.status.event_bus.EventBus.broadcast")

    await watcher.package_remove(package_ahriman.base)
    cache_mock.assert_called_once_with(package_ahriman.base)
    broadcast_mock.assert_called_once_with(EventType.PackageRemoved, package_ahriman.base)


async def test_package_status_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package status only for known package
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_status_update")
    broadcast_mock = mocker.patch("ahriman.core.status.event_bus.EventBus.broadcast")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    await watcher.package_status_update(package_ahriman.base, BuildStatusEnum.Success)
    cache_mock.assert_called_once_with(package_ahriman.base, pytest.helpers.anyvar(int))
    package, status = watcher._known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Success
    broadcast_mock.assert_called_once_with(
        EventType.PackageStatusChanged, package_ahriman.base, status=BuildStatusEnum.Success.value,
    )


async def test_package_status_update_preserves_hold(watcher: Watcher, package_ahriman: Package,
                                                    mocker: MockerFixture) -> None:
    """
    must preserve hold status on package status update
    """
    mocker.patch("ahriman.core.status.local_client.LocalClient.package_status_update")
    mocker.patch("ahriman.core.status.event_bus.EventBus.broadcast")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus(is_held=True))}

    await watcher.package_status_update(package_ahriman.base, BuildStatusEnum.Success)
    _, status = watcher._known[package_ahriman.base]
    assert status.is_held is True


async def test_package_status_update_unknown(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail on unknown package status update only
    """
    with pytest.raises(UnknownPackageError):
        await watcher.package_status_update(package_ahriman.base, BuildStatusEnum.Unknown)


async def test_package_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add package to cache
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_update")
    broadcast_mock = mocker.patch("ahriman.core.status.event_bus.EventBus.broadcast")

    await watcher.package_update(package_ahriman, BuildStatusEnum.Unknown)
    assert await watcher.packages()
    cache_mock.assert_called_once_with(package_ahriman, pytest.helpers.anyvar(int))
    broadcast_mock.assert_called_once_with(
        EventType.PackageUpdated, package_ahriman.base,
        status=BuildStatusEnum.Unknown.value, version=package_ahriman.version,
    )


async def test_package_update_preserves_hold(watcher: Watcher, package_ahriman: Package,
                                             mocker: MockerFixture) -> None:
    """
    must preserve hold status on package update
    """
    mocker.patch("ahriman.core.status.local_client.LocalClient.package_update")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus(is_held=True))}

    await watcher.package_update(package_ahriman, BuildStatusEnum.Success)
    _, status = watcher._known[package_ahriman.base]
    assert status.is_held is True


async def test_packages(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must return list of available packages
    """
    assert not await watcher.packages()

    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}
    assert await watcher.packages()


async def test_shutdown(watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must gracefully shutdown watcher
    """
    shutdown_mock = mocker.patch("ahriman.core.status.event_bus.EventBus.shutdown")
    await watcher.shutdown()
    shutdown_mock.assert_called_once_with()


async def test_status_update(watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must update service status
    """
    broadcast_mock = mocker.patch("ahriman.core.status.event_bus.EventBus.broadcast")

    await watcher.status_update(BuildStatusEnum.Success)
    assert watcher.status.status == BuildStatusEnum.Success
    broadcast_mock.assert_called_once_with(EventType.ServiceStatusChanged, None, status=BuildStatusEnum.Success.value)


def test_call(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must return self instance if package exists
    """
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}
    assert watcher(package_ahriman.base)


def test_call_skip(watcher: Watcher) -> None:
    """
    must return self instance if no package base set
    """
    assert watcher(None)


def test_call_failed(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must raise UnknownPackage
    """
    with pytest.raises(UnknownPackageError):
        assert watcher(package_ahriman.base)
