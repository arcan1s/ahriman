import pytest

from pytest_mock import MockerFixture
from sqlite3 import Connection

from ahriman.core.configuration import Configuration
from ahriman.core.database.migrations.m008_packagers import migrate_data, migrate_package_base_packager, steps
from ahriman.models.package import Package


def test_migration_packagers() -> None:
    """
    migration must not be empty
    """
    assert steps


def test_migrate_data(connection: Connection, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must perform data migration
    """
    depends_mock = mocker.patch("ahriman.core.database.migrations.m008_packagers.migrate_package_base_packager")
    migrate_data(connection, configuration)
    depends_mock.assert_called_once_with(connection, configuration)


def test_migrate_package_base_packager(connection: Connection, configuration: Configuration, package_ahriman: Package,
                                       mocker: MockerFixture) -> None:
    """
    must update packagers
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.iterdir", return_value=[package_ahriman.packages[package_ahriman.base].filepath])
    package_mock = mocker.patch("ahriman.models.package.Package.from_archive", return_value=package_ahriman)

    migrate_package_base_packager(connection, configuration)
    package_mock.assert_called_once_with(
        package_ahriman.packages[package_ahriman.base].filepath, pytest.helpers.anyvar(int), remote=None)
    connection.executemany.assert_called_once_with(pytest.helpers.anyvar(str, strict=True), [{
        "package_base": package_ahriman.base,
        "packager": package_ahriman.packager,
    }])


def test_migrate_package_depends_skip(connection: Connection, configuration: Configuration,
                                      mocker: MockerFixture) -> None:
    """
    must skip update packagers if no repository directory found
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    migrate_package_base_packager(connection, configuration)
    connection.executemany.assert_not_called()
