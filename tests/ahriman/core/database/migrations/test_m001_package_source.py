import pytest

from pytest_mock import MockerFixture
from sqlite3 import Connection
from unittest.mock import call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.core.database.migrations.m001_package_source import migrate_data, migrate_package_remotes, steps
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.repository_paths import RepositoryPaths


def test_migration_package_source() -> None:
    """
    migration must not be empty
    """
    assert steps


def test_migrate_data(connection: Connection, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must perform data migration
    """
    remotes = mocker.patch("ahriman.core.database.migrations.m001_package_source.migrate_package_remotes")
    migrate_data(connection, configuration)
    remotes.assert_called_once_with(connection, configuration.repository_paths)


def test_migrate_package_remotes(package_ahriman: Package, connection: Connection, repository_paths: RepositoryPaths,
                                 mocker: MockerFixture) -> None:
    """
    must put package remotes to database
    """
    connection.execute.return_value = [{
        "package_base": package_ahriman.base,
        "version": package_ahriman.version,
        "source": PackageSource.AUR,
    }]
    mocker.patch("pathlib.Path.exists", return_value=False)

    migrate_package_remotes(connection, repository_paths)
    connection.execute.assert_has_calls([
        MockCall(pytest.helpers.anyvar(str, strict=True)),
        MockCall(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int)),
    ])


def test_migrate_package_remotes_has_local(package_ahriman: Package, connection: Connection,
                                           repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must skip processing for packages which have local cache
    """
    connection.execute.return_value = [{
        "package_base": package_ahriman.base,
        "version": package_ahriman.version,
        "source": PackageSource.AUR,
    }]
    mocker.patch("pathlib.Path.exists", return_value=True)

    migrate_package_remotes(connection, repository_paths)
    connection.execute.assert_called_once_with(pytest.helpers.anyvar(str, strict=True))


def test_migrate_package_remotes_vcs(package_ahriman: Package, connection: Connection,
                                     repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must process VCS packages with local cache
    """
    connection.execute.return_value = [{
        "package_base": package_ahriman.base,
        "version": package_ahriman.version,
        "source": PackageSource.AUR,
    }]
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch.object(Package, "is_vcs", True)

    migrate_package_remotes(connection, repository_paths)
    connection.execute.assert_has_calls([
        MockCall(pytest.helpers.anyvar(str, strict=True)),
        MockCall(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int)),
    ])
