import pytest

from pytest_mock import MockerFixture
from sqlite3 import Connection
from unittest.mock import call as MockCall

from ahriman.core.database import SQLite
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.remote_source import RemoteSource


def test_package_remove_package_base(database: SQLite, connection: Connection) -> None:
    """
    must remove package base
    """
    database._package_remove_package_base(connection, "package")
    connection.execute.assert_has_calls([
        MockCall(pytest.helpers.anyvar(str, strict=True), {"package_base": "package"}),
        MockCall(pytest.helpers.anyvar(str, strict=True), {"package_base": "package"}),
    ])


def test_package_remove_packages(database: SQLite, connection: Connection, package_ahriman: Package) -> None:
    """
    must remove packages belong to base
    """
    database._package_remove_packages(connection, package_ahriman.base, package_ahriman.packages.keys())
    connection.execute.assert_called_once_with(
        pytest.helpers.anyvar(str, strict=True), {"package_base": package_ahriman.base})
    connection.executemany.assert_called_once_with(pytest.helpers.anyvar(str, strict=True), [])


def test_package_update_insert_base(database: SQLite, connection: Connection, package_ahriman: Package) -> None:
    """
    must insert base package
    """
    database._package_update_insert_base(connection, package_ahriman)
    connection.execute.assert_called_once_with(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int))


def test_package_update_insert_packages(database: SQLite, connection: Connection, package_ahriman: Package) -> None:
    """
    must insert single packages
    """
    database._package_update_insert_packages(connection, package_ahriman)
    connection.executemany(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int))


def test_package_update_insert_status(database: SQLite, connection: Connection, package_ahriman: Package) -> None:
    """
    must insert single package status
    """
    database._package_update_insert_status(connection, package_ahriman.base, BuildStatus())
    connection.execute(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int))


def test_packages_get_select_package_bases(database: SQLite, connection: Connection) -> None:
    """
    must select all bases
    """
    database._packages_get_select_package_bases(connection)
    connection.execute(pytest.helpers.anyvar(str, strict=True))


def test_packages_get_select_packages(database: SQLite, connection: Connection, package_ahriman: Package) -> None:
    """
    must select all packages
    """
    database._packages_get_select_packages(connection, {package_ahriman.base: package_ahriman})
    connection.execute(pytest.helpers.anyvar(str, strict=True))


def test_packages_get_select_packages_skip(database: SQLite, connection: Connection, package_ahriman: Package) -> None:
    """
    must skip unknown packages
    """
    view = {"package_base": package_ahriman.base}
    for package, properties in package_ahriman.packages.items():
        view.update({"package": package})
        view.update(properties.view())
    connection.execute.return_value = [{"package_base": "random name"}, view]

    database._packages_get_select_packages(connection, {package_ahriman.base: package_ahriman})


def test_packages_get_select_statuses(database: SQLite, connection: Connection) -> None:
    """
    must select all statuses
    """
    database._packages_get_select_statuses(connection)
    connection.execute(pytest.helpers.anyvar(str, strict=True))


def test_package_remove(database: SQLite, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must totally remove package from the database
    """
    remove_package_mock = mocker.patch("ahriman.core.database.SQLite._package_remove_package_base")
    remove_packages_mock = mocker.patch("ahriman.core.database.SQLite._package_remove_packages")

    database.package_remove(package_ahriman.base)
    remove_package_mock.assert_called_once_with(pytest.helpers.anyvar(int), package_ahriman.base)
    remove_packages_mock.assert_called_once_with(pytest.helpers.anyvar(int), package_ahriman.base, [])


def test_package_update(database: SQLite, package_ahriman: Package, mocker: MockerFixture):
    """
    must update package status
    """
    status = BuildStatus()
    insert_base_mock = mocker.patch("ahriman.core.database.SQLite._package_update_insert_base")
    insert_status_mock = mocker.patch("ahriman.core.database.SQLite._package_update_insert_status")
    insert_packages_mock = mocker.patch("ahriman.core.database.SQLite._package_update_insert_packages")
    remove_packages_mock = mocker.patch("ahriman.core.database.SQLite._package_remove_packages")

    database.package_update(package_ahriman, status)
    insert_base_mock.assert_called_once_with(pytest.helpers.anyvar(int), package_ahriman)
    insert_status_mock.assert_called_once_with(pytest.helpers.anyvar(int), package_ahriman.base, status)
    insert_packages_mock.assert_called_once_with(pytest.helpers.anyvar(int), package_ahriman)
    remove_packages_mock.assert_called_once_with(
        pytest.helpers.anyvar(int), package_ahriman.base, package_ahriman.packages.keys())


def test_packages_get(database: SQLite, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return all packages
    """
    select_bases_mock = mocker.patch("ahriman.core.database.SQLite._packages_get_select_package_bases",
                                     return_value={package_ahriman.base: package_ahriman})
    select_packages_mock = mocker.patch("ahriman.core.database.SQLite._packages_get_select_packages")
    select_statuses_mock = mocker.patch("ahriman.core.database.SQLite._packages_get_select_statuses")

    database.packages_get()
    select_bases_mock.assert_called_once_with(pytest.helpers.anyvar(int))
    select_statuses_mock.assert_called_once_with(pytest.helpers.anyvar(int))
    select_packages_mock.assert_called_once_with(pytest.helpers.anyvar(int), {package_ahriman.base: package_ahriman})


def test_package_update_get(database: SQLite, package_ahriman: Package) -> None:
    """
    must insert and retrieve package
    """
    status = BuildStatus()
    database.package_update(package_ahriman, status)
    assert next((db_package, db_status)
                for db_package, db_status in database.packages_get()
                if db_package.base == package_ahriman.base) == (package_ahriman, status)


def test_package_update_remove_get(database: SQLite, package_ahriman: Package) -> None:
    """
    must insert, remove and retrieve package
    """
    status = BuildStatus()
    database.package_update(package_ahriman, status)
    database.package_remove(package_ahriman.base)
    assert not database.packages_get()


def test_package_update_update(database: SQLite, package_ahriman: Package) -> None:
    """
    must perform update for existing package
    """
    database.package_update(package_ahriman, BuildStatus())
    database.package_update(package_ahriman, BuildStatus(BuildStatusEnum.Failed))
    assert next(db_status.status
                for db_package, db_status in database.packages_get()
                if db_package.base == package_ahriman.base) == BuildStatusEnum.Failed


def test_remote_update_get(database: SQLite, package_ahriman: Package) -> None:
    """
    must insert and retrieve package remote
    """
    database.remote_update(package_ahriman)
    assert database.remotes_get()[package_ahriman.base] == package_ahriman.remote


def test_remote_update_update(database: SQLite, package_ahriman: Package) -> None:
    """
    must perform package remote update for existing package
    """
    database.remote_update(package_ahriman)
    remote_source = RemoteSource.from_source(PackageSource.Repository, package_ahriman.base, "community")
    package_ahriman.remote = remote_source

    database.remote_update(package_ahriman)
    assert database.remotes_get()[package_ahriman.base] == remote_source
