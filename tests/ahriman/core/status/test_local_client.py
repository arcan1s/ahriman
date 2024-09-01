import logging
import pytest

from pytest_mock import MockerFixture

from ahriman.core.status.local_client import LocalClient
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.changes import Changes
from ahriman.models.dependencies import Dependencies
from ahriman.models.event import Event, EventType
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch


def test_event_add(local_client: LocalClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add new event
    """
    event_mock = mocker.patch("ahriman.core.database.SQLite.event_insert")
    event = Event(EventType.PackageUpdated, package_ahriman.base)

    local_client.event_add(event)
    event_mock.assert_called_once_with(event, local_client.repository_id)


def test_event_get(local_client: LocalClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must retrieve events
    """
    event_mock = mocker.patch("ahriman.core.database.SQLite.event_get")
    local_client.event_get(EventType.PackageUpdated, package_ahriman.base, from_date=10, to_date=20, limit=1, offset=2)
    event_mock.assert_called_once_with(EventType.PackageUpdated, package_ahriman.base, 10, 20, 1, 2,
                                       local_client.repository_id)


def test_package_changes_get(local_client: LocalClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must retrieve package changes
    """
    changes_mock = mocker.patch("ahriman.core.database.SQLite.changes_get")
    local_client.package_changes_get(package_ahriman.base)
    changes_mock.assert_called_once_with(package_ahriman.base, local_client.repository_id)


def test_package_changes_update(local_client: LocalClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package changes
    """
    changes_mock = mocker.patch("ahriman.core.database.SQLite.changes_insert")
    changes = Changes()

    local_client.package_changes_update(package_ahriman.base, changes)
    changes_mock.assert_called_once_with(package_ahriman.base, changes, local_client.repository_id)


def test_package_dependencies_get(local_client: LocalClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must retrieve package dependencies
    """
    dependencies_mock = mocker.patch("ahriman.core.database.SQLite.dependencies_get")
    local_client.package_dependencies_get(package_ahriman.base)
    dependencies_mock.assert_called_once_with(package_ahriman.base, local_client.repository_id)


def test_package_dependencies_update(
        local_client: LocalClient,
        package_ahriman: Package,
        mocker: MockerFixture) -> None:
    """
    must update package dependencies
    """
    dependencies_mock = mocker.patch("ahriman.core.database.SQLite.dependencies_insert")
    local_client.package_dependencies_update(package_ahriman.base, Dependencies())
    dependencies_mock.assert_called_once_with(package_ahriman.base, Dependencies(), local_client.repository_id)


def test_package_get(local_client: LocalClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must retrieve packages
    """
    result = [(package_ahriman, BuildStatus())]
    package_mock = mocker.patch("ahriman.core.database.SQLite.packages_get", return_value=result)
    assert local_client.package_get(None) == result
    package_mock.assert_called_once_with(local_client.repository_id)


def test_package_get_package(local_client: LocalClient, package_ahriman: Package, package_python_schedule: Package,
                             mocker: MockerFixture) -> None:
    """
    must retrieve specific package
    """
    result = [(package_ahriman, BuildStatus()), (package_python_schedule, BuildStatus())]
    package_mock = mocker.patch("ahriman.core.database.SQLite.packages_get", return_value=result)
    assert local_client.package_get(package_ahriman.base) == [result[0]]
    package_mock.assert_called_once_with(local_client.repository_id)


def test_package_logs_add(local_client: LocalClient, package_ahriman: Package, log_record: logging.LogRecord,
                          mocker: MockerFixture) -> None:
    """
    must add package logs
    """
    logs_mock = mocker.patch("ahriman.core.database.SQLite.logs_insert")
    log_record_id = LogRecordId(package_ahriman.base, package_ahriman.version)

    local_client.package_logs_add(log_record_id, log_record.created, log_record.getMessage())
    logs_mock.assert_called_once_with(log_record_id, log_record.created, log_record.getMessage(),
                                      local_client.repository_id)


def test_package_logs_get(local_client: LocalClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must retrieve package logs
    """
    logs_mock = mocker.patch("ahriman.core.database.SQLite.logs_get")
    local_client.package_logs_get(package_ahriman.base, 1, 2)
    logs_mock.assert_called_once_with(package_ahriman.base, 1, 2, local_client.repository_id)


def test_package_logs_remove(local_client: LocalClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package logs
    """
    logs_mock = mocker.patch("ahriman.core.database.SQLite.logs_remove")
    local_client.package_logs_remove(package_ahriman.base, package_ahriman.version)
    logs_mock.assert_called_once_with(package_ahriman.base, package_ahriman.version, local_client.repository_id)


def test_package_patches_get(local_client: LocalClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must retrieve package patches
    """
    patches_mock = mocker.patch("ahriman.core.database.SQLite.patches_list")
    local_client.package_patches_get(package_ahriman.base, None)
    patches_mock.assert_called_once_with(package_ahriman.base, None)


def test_package_patches_get_key(local_client: LocalClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must retrieve package patches for specific patch name
    """
    patches_mock = mocker.patch("ahriman.core.database.SQLite.patches_list")
    local_client.package_patches_get(package_ahriman.base, "key")
    patches_mock.assert_called_once_with(package_ahriman.base, ["key"])


def test_package_patches_remove(local_client: LocalClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package patches
    """
    patches_mock = mocker.patch("ahriman.core.database.SQLite.patches_remove")
    local_client.package_patches_remove(package_ahriman.base, None)
    patches_mock.assert_called_once_with(package_ahriman.base, None)


def test_package_patches_remove_key(local_client: LocalClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package specific package patch
    """
    patches_mock = mocker.patch("ahriman.core.database.SQLite.patches_remove")
    local_client.package_patches_remove(package_ahriman.base, "key")
    patches_mock.assert_called_once_with(package_ahriman.base, ["key"])


def test_package_patches_update(local_client: LocalClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add package patches
    """
    patches_mock = mocker.patch("ahriman.core.database.SQLite.patches_insert")
    patch = PkgbuildPatch("key", "value")

    local_client.package_patches_update(package_ahriman.base, patch)
    patches_mock.assert_called_once_with(package_ahriman.base, [patch])


def test_package_remove(local_client: LocalClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package
    """
    package_mock = mocker.patch("ahriman.core.database.SQLite.package_clear")
    local_client.package_remove(package_ahriman.base)
    package_mock.assert_called_once_with(package_ahriman.base)


def test_package_status_update(local_client: LocalClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package status
    """
    status_mock = mocker.patch("ahriman.core.database.SQLite.status_update")
    local_client.package_status_update(package_ahriman.base, BuildStatusEnum.Success)
    status_mock.assert_called_once_with(package_ahriman.base, pytest.helpers.anyvar(int), local_client.repository_id)


def test_package_update(local_client: LocalClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process package addition
    """
    package_mock = mocker.patch("ahriman.core.database.SQLite.package_update")
    status_mock = mocker.patch("ahriman.core.database.SQLite.status_update")

    local_client.package_update(package_ahriman, BuildStatusEnum.Success)
    package_mock.assert_called_once_with(package_ahriman, local_client.repository_id)
    status_mock.assert_called_once_with(package_ahriman.base, pytest.helpers.anyvar(int), local_client.repository_id)
