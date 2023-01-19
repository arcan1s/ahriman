import pytest

from pytest_mock import MockerFixture
from sqlite3 import Connection
from unittest.mock import MagicMock, call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.core.database.migrations import Migrations
from ahriman.models.migration import Migration
from ahriman.models.migration_result import MigrationResult


def test_migrate(connection: Connection, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must perform migrations
    """
    run_mock = mocker.patch("ahriman.core.database.migrations.Migrations.run")
    Migrations.migrate(connection, configuration)
    run_mock.assert_called_once_with()


def test_migration(migrations: Migrations, connection: Connection) -> None:
    """
    must perform single migration
    """
    migrate_data_mock = MagicMock()
    cursor = MagicMock()
    migration = Migration(index=0, name="test", steps=["select 1"], migrate_data=migrate_data_mock)

    migrations.migration(cursor, migration)
    cursor.execute.assert_called_once_with("select 1")
    migrate_data_mock.assert_called_once_with(migrations.connection, migrations.configuration)


def test_migrations(migrations: Migrations) -> None:
    """
    must retrieve migrations
    """
    assert migrations.migrations()


def test_run_skip(migrations: Migrations, mocker: MockerFixture) -> None:
    """
    must skip migration if version is the same
    """
    mocker.patch.object(MigrationResult, "is_outdated", False)

    migrations.run()
    migrations.connection.cursor.assert_not_called()


def test_run(migrations: Migrations, mocker: MockerFixture) -> None:
    """
    must run migration
    """
    migration = Migration(index=0, name="test", steps=["select 1"], migrate_data=MagicMock())
    cursor = MagicMock()
    mocker.patch("ahriman.core.database.migrations.Migrations.user_version", return_value=0)
    mocker.patch("ahriman.core.database.migrations.Migrations.migrations", return_value=[migration])
    migrations.connection.cursor.return_value = cursor
    migration_mock = mocker.patch("ahriman.core.database.migrations.Migrations.migration")
    validate_mock = mocker.patch("ahriman.models.migration_result.MigrationResult.validate")

    migrations.run()
    validate_mock.assert_called_once_with()
    cursor.execute.assert_has_calls([
        MockCall("begin exclusive"),
        MockCall("pragma user_version = 1"),
        MockCall("commit"),
    ])
    cursor.close.assert_called_once_with()
    migration_mock.assert_called_once_with(cursor, migration)


def test_run_migration_exception(migrations: Migrations, mocker: MockerFixture) -> None:
    """
    must roll back and close cursor on exception during migration
    """
    cursor = MagicMock()
    mocker.patch("logging.Logger.info", side_effect=Exception())
    mocker.patch("ahriman.core.database.migrations.Migrations.user_version", return_value=0)
    mocker.patch("ahriman.core.database.migrations.Migrations.migrations",
                 return_value=[Migration(index=0, name="test", steps=["select 1"], migrate_data=MagicMock())])
    mocker.patch("ahriman.models.migration_result.MigrationResult.validate")
    migrations.connection.cursor.return_value = cursor

    with pytest.raises(Exception):
        migrations.run()
    cursor.execute.assert_has_calls([
        MockCall("begin exclusive"),
        MockCall("rollback"),
    ])
    cursor.close.assert_called_once_with()


def test_run_sql_exception(migrations: Migrations, mocker: MockerFixture) -> None:
    """
    must close cursor on general migration error
    """
    cursor = MagicMock()
    cursor.execute.side_effect = Exception()
    mocker.patch("ahriman.core.database.migrations.Migrations.user_version", return_value=0)
    mocker.patch("ahriman.core.database.migrations.Migrations.migrations",
                 return_value=[Migration(index=0, name="test", steps=["select 1"], migrate_data=MagicMock())])
    mocker.patch("ahriman.models.migration_result.MigrationResult.validate")
    migrations.connection.cursor.return_value = cursor

    with pytest.raises(Exception):
        migrations.run()
    cursor.close.assert_called_once_with()


def test_user_version(migrations: Migrations) -> None:
    """
    must correctly extract current migration version
    """
    cursor = MagicMock()
    cursor.fetchone.return_value = {"user_version": 42}
    migrations.connection.execute.return_value = cursor

    version = migrations.user_version()
    migrations.connection.execute.assert_called_once_with("pragma user_version")
    assert version == 42
