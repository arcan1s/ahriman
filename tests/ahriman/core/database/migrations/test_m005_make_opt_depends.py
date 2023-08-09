import pytest

from pytest_mock import MockerFixture
from sqlite3 import Connection

from ahriman.core.configuration import Configuration
from ahriman.core.database.migrations.m005_make_opt_depends import migrate_data, migrate_package_depends, steps
from ahriman.models.package import Package


def test_migration_make_opt_depends() -> None:
    """
    migration must not be empty
    """
    assert steps


def test_migrate_data(connection: Connection, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must perform data migration
    """
    depends_mock = mocker.patch("ahriman.core.database.migrations.m005_make_opt_depends.migrate_package_depends")
    migrate_data(connection, configuration)
    depends_mock.assert_called_once_with(connection, configuration)


def test_migrate_package_depends(connection: Connection, configuration: Configuration, package_ahriman: Package,
                                 mocker: MockerFixture) -> None:
    """
    must update make and opt depends list
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.iterdir", return_value=[package_ahriman.packages[package_ahriman.base].filepath])
    package_mock = mocker.patch("ahriman.models.package.Package.from_archive", return_value=package_ahriman)

    migrate_package_depends(connection, configuration)
    package_mock.assert_called_once_with(
        package_ahriman.packages[package_ahriman.base].filepath, pytest.helpers.anyvar(int))
    connection.executemany.assert_called_once_with(pytest.helpers.anyvar(str, strict=True), [{
        "make_depends": package_ahriman.packages[package_ahriman.base].make_depends,
        "opt_depends": package_ahriman.packages[package_ahriman.base].opt_depends,
        "package": package_ahriman.base,
    }])


def test_migrate_package_depends_skip(connection: Connection, configuration: Configuration,
                                      mocker: MockerFixture) -> None:
    """
    must skip update make and opt depends list if no repository directory found
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    migrate_package_depends(connection, configuration)
    connection.executemany.assert_not_called()
