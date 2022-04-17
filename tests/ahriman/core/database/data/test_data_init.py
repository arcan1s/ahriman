from pytest_mock import MockerFixture
from sqlite3 import Connection

from ahriman.core.configuration import Configuration
from ahriman.core.database.data import migrate_data
from ahriman.models.migration_result import MigrationResult
from ahriman.models.repository_paths import RepositoryPaths


def test_migrate_data_initial(connection: Connection, configuration: Configuration,
                              repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must perform initial migration
    """
    packages = mocker.patch("ahriman.core.database.data.migrate_package_statuses")
    patches = mocker.patch("ahriman.core.database.data.migrate_patches")
    users = mocker.patch("ahriman.core.database.data.migrate_users_data")

    migrate_data(MigrationResult(old_version=0, new_version=900), connection, configuration)
    packages.assert_called_once_with(connection, repository_paths)
    patches.assert_called_once_with(connection, repository_paths)
    users.assert_called_once_with(connection, configuration)


def test_migrate_data_skip(connection: Connection, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must not migrate data if version is up-to-date
    """
    packages = mocker.patch("ahriman.core.database.data.migrate_package_statuses")
    users = mocker.patch("ahriman.core.database.data.migrate_users_data")

    migrate_data(MigrationResult(old_version=900, new_version=900), connection, configuration)
    packages.assert_not_called()
    users.assert_not_called()
