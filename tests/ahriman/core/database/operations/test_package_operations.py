import pytest

from pytest_mock import MockerFixture
from sqlite3 import Connection
from unittest.mock import call as MockCall

from ahriman.core.database import SQLite
from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package


def test_package_remove_package_base(database: SQLite, connection: Connection) -> None:
    """
    must remove package base
    """
    database._package_remove_package_base(connection, "package", database._repository_id)
    args = {
        "package_base": "package",
        "repository": database._repository_id.id,
    }
    connection.execute.assert_has_calls([
        MockCall(pytest.helpers.anyvar(str, strict=True), args),
        MockCall(pytest.helpers.anyvar(str, strict=True), args),
    ])


def test_package_remove_packages(database: SQLite, connection: Connection, package_ahriman: Package) -> None:
    """
    must remove packages belong to base
    """
    database._package_remove_packages(connection, package_ahriman.base, package_ahriman.packages.keys(),
                                      database._repository_id)
    connection.execute.assert_called_once_with(
        pytest.helpers.anyvar(str, strict=True), {
            "package_base": package_ahriman.base,
            "repository": database._repository_id.id,
        })
    connection.executemany.assert_called_once_with(pytest.helpers.anyvar(str, strict=True), [])


def test_package_update_insert_base(database: SQLite, connection: Connection, package_ahriman: Package) -> None:
    """
    must insert base package
    """
    database._package_update_insert_base(connection, package_ahriman, database._repository_id)
    connection.execute.assert_called_once_with(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int))


def test_package_update_insert_packages(database: SQLite, connection: Connection, package_ahriman: Package) -> None:
    """
    must insert single packages
    """
    database._package_update_insert_packages(connection, package_ahriman, database._repository_id)
    connection.executemany(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int))


def test_package_update_insert_packages_no_arch(database: SQLite, connection: Connection,
                                                package_ahriman: Package) -> None:
    """
    must skip package insertion if no package architecture set
    """
    package_ahriman.packages[package_ahriman.base].architecture = None
    database._package_update_insert_packages(connection, package_ahriman, database._repository_id)
    connection.executemany(pytest.helpers.anyvar(str, strict=True), [])


def test_packages_get_select_package_bases(database: SQLite, connection: Connection) -> None:
    """
    must select all bases
    """
    database._packages_get_select_package_bases(connection, database._repository_id)
    connection.execute(pytest.helpers.anyvar(str, strict=True))


def test_packages_get_select_packages(database: SQLite, connection: Connection, package_ahriman: Package) -> None:
    """
    must select all packages
    """
    database._packages_get_select_packages(connection, {package_ahriman.base: package_ahriman},
                                           database._repository_id)
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

    database._packages_get_select_packages(connection, {package_ahriman.base: package_ahriman},
                                           database._repository_id)


def test_packages_get_select_statuses(database: SQLite, connection: Connection) -> None:
    """
    must select all statuses
    """
    database._packages_get_select_statuses(connection, database._repository_id)
    connection.execute(pytest.helpers.anyvar(str, strict=True))


def test_package_remove(database: SQLite, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must totally remove package from the database
    """
    remove_package_mock = mocker.patch("ahriman.core.database.SQLite._package_remove_package_base")
    remove_packages_mock = mocker.patch("ahriman.core.database.SQLite._package_remove_packages")

    database.package_remove(package_ahriman.base)
    remove_package_mock.assert_called_once_with(pytest.helpers.anyvar(int), package_ahriman.base,
                                                database._repository_id)
    remove_packages_mock.assert_called_once_with(pytest.helpers.anyvar(int), package_ahriman.base, [],
                                                 database._repository_id)


def test_package_update(database: SQLite, package_ahriman: Package, mocker: MockerFixture):
    """
    must update package status
    """
    insert_base_mock = mocker.patch("ahriman.core.database.SQLite._package_update_insert_base")
    insert_packages_mock = mocker.patch("ahriman.core.database.SQLite._package_update_insert_packages")
    remove_packages_mock = mocker.patch("ahriman.core.database.SQLite._package_remove_packages")

    database.package_update(package_ahriman)
    insert_base_mock.assert_called_once_with(pytest.helpers.anyvar(int), package_ahriman, database._repository_id)
    insert_packages_mock.assert_called_once_with(pytest.helpers.anyvar(int), package_ahriman,
                                                 database._repository_id)
    remove_packages_mock.assert_called_once_with(pytest.helpers.anyvar(int), package_ahriman.base,
                                                 package_ahriman.packages.keys(), database._repository_id)


def test_packages_get(database: SQLite, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return all packages
    """
    select_bases_mock = mocker.patch("ahriman.core.database.SQLite._packages_get_select_package_bases",
                                     return_value={package_ahriman.base: package_ahriman})
    select_packages_mock = mocker.patch("ahriman.core.database.SQLite._packages_get_select_packages")
    select_statuses_mock = mocker.patch("ahriman.core.database.SQLite._packages_get_select_statuses")

    database.packages_get()
    select_bases_mock.assert_called_once_with(pytest.helpers.anyvar(int), database._repository_id)
    select_statuses_mock.assert_called_once_with(pytest.helpers.anyvar(int), database._repository_id)
    select_packages_mock.assert_called_once_with(pytest.helpers.anyvar(int), {package_ahriman.base: package_ahriman},
                                                 database._repository_id)


def test_package_update_get(database: SQLite, package_ahriman: Package) -> None:
    """
    must insert and retrieve package
    """
    status = BuildStatus()
    database.package_update(package_ahriman)
    database.status_update(package_ahriman.base, status)
    assert next((db_package, db_status)
                for db_package, db_status in database.packages_get()
                if db_package.base == package_ahriman.base) == (package_ahriman, status)


def test_package_update_remove_get(database: SQLite, package_ahriman: Package) -> None:
    """
    must insert, remove and retrieve package
    """
    database.package_update(package_ahriman)
    database.package_remove(package_ahriman.base)
    assert not database.packages_get()


def test_package_update_update(database: SQLite, package_ahriman: Package) -> None:
    """
    must perform update for existing package
    """
    database.package_update(package_ahriman)
    package_ahriman.version = "1.0.0"
    database.package_update(package_ahriman)
    assert next(db_package.version
                for db_package, _ in database.packages_get()
                if db_package.base == package_ahriman.base) == package_ahriman.version


def test_status_update(database: SQLite, package_ahriman: Package) -> None:
    """
    must insert single package status
    """
    status = BuildStatus()

    database.package_update(package_ahriman, database._repository_id)
    database.status_update(package_ahriman.base, status, database._repository_id)
    assert database.packages_get(database._repository_id) == [(package_ahriman, status)]
