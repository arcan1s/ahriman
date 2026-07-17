import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from sqlite3 import Connection
from unittest.mock import call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.core.database.migrations.m000_initial import migrate_data, migrate_package_statuses, migrate_patches, \
    migrate_users_data, steps
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


def test_migration_initial() -> None:
    """
    migration must not be empty
    """
    assert steps


def test_migrate_data(connection: Connection, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must perform data migration
    """
    packages = mocker.patch("ahriman.core.database.migrations.m000_initial.migrate_package_statuses")
    patches = mocker.patch("ahriman.core.database.migrations.m000_initial.migrate_patches")
    users = mocker.patch("ahriman.core.database.migrations.m000_initial.migrate_users_data")

    migrate_data(connection, configuration)
    packages.assert_called_once_with(connection, configuration.repository_paths)
    patches.assert_called_once_with(connection, configuration.repository_paths)
    users.assert_called_once_with(connection, configuration)


def test_migrate_package_statuses(connection: Connection, package_ahriman: Package, repository_paths: RepositoryPaths,
                                  mocker: MockerFixture) -> None:
    """
    must migrate packages to database
    """
    response = {"packages": [pytest.helpers.get_package_status_extended(package_ahriman)]}

    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.open")
    mocker.patch("json.load", return_value=response)

    migrate_package_statuses(connection, repository_paths)
    connection.execute.assert_has_calls([
        MockCall(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int)),
        MockCall(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int)),
    ])
    connection.executemany.assert_has_calls([
        MockCall(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int)),
    ])


def test_migrate_package_statuses_skip(connection: Connection, repository_paths: RepositoryPaths,
                                       mocker: MockerFixture) -> None:
    """
    must skip packages migration if no cache file found
    """
    mocker.patch("pathlib.Path.is_file", return_value=False)
    migrate_package_statuses(connection, repository_paths)


def test_migrate_patches(connection: Connection, repository_paths: RepositoryPaths,
                         package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must perform migration for patches
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=True)
    iterdir_mock = mocker.patch("pathlib.Path.iterdir", return_value=[Path(package_ahriman.base)])
    read_mock = mocker.patch("pathlib.Path.read_text", return_value="patch")

    migrate_patches(connection, repository_paths)
    iterdir_mock.assert_called_once_with()
    read_mock.assert_called_once_with(encoding="utf8")
    connection.execute.assert_called_once_with(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int))


def test_migrate_patches_skip(connection: Connection, repository_paths: RepositoryPaths,
                              mocker: MockerFixture) -> None:
    """
    must skip patches migration in case if no root found
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    iterdir_mock = mocker.patch("pathlib.Path.iterdir")

    migrate_patches(connection, repository_paths)
    iterdir_mock.assert_not_called()


def test_migrate_patches_no_patch(connection: Connection, repository_paths: RepositoryPaths,
                                  package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must skip package if no match found
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=False)
    iterdir_mock = mocker.patch("pathlib.Path.iterdir", return_value=[Path(package_ahriman.base)])
    read_mock = mocker.patch("pathlib.Path.read_text")

    migrate_patches(connection, repository_paths)
    iterdir_mock.assert_called_once_with()
    read_mock.assert_not_called()


def test_migrate_users_data(connection: Connection, configuration: Configuration) -> None:
    """
    must put users to database
    """
    configuration.set_option("auth:read", "user1", "password1")
    configuration.set_option("auth:write", "user2", "password2")

    migrate_users_data(connection, configuration)
    connection.execute.assert_has_calls([
        MockCall(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int)),
        MockCall(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int)),
    ])
