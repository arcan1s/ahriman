import pytest

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.models.repository_id import RepositoryId


def test_load(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must correctly load instance
    """
    init_mock = mocker.patch("ahriman.core.database.SQLite.init")
    SQLite.load(configuration)
    init_mock.assert_called_once_with()


def test_init(database: SQLite, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run migrations on init
    """
    migrate_schema_mock = mocker.patch("ahriman.core.database.migrations.Migrations.migrate")
    database.init()
    migrate_schema_mock.assert_called_once_with(pytest.helpers.anyvar(int), database._configuration)


def test_init_skip_migration(database: SQLite, mocker: MockerFixture) -> None:
    """
    must skip migrations if option is set
    """
    database._configuration.set_option("settings", "apply_migrations", "no")
    migrate_schema_mock = mocker.patch("ahriman.core.database.migrations.Migrations.migrate")

    database.init()
    migrate_schema_mock.assert_not_called()


def test_package_clear(database: SQLite, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must clear package data
    """
    build_queue_mock = mocker.patch("ahriman.core.database.SQLite.build_queue_clear")
    patches_mock = mocker.patch("ahriman.core.database.SQLite.patches_remove")
    logs_mock = mocker.patch("ahriman.core.database.SQLite.logs_remove")
    changes_mock = mocker.patch("ahriman.core.database.SQLite.changes_remove")
    dependencies_mock = mocker.patch("ahriman.core.database.SQLite.dependencies_remove")
    package_mock = mocker.patch("ahriman.core.database.SQLite.package_remove")
    tree_clear_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_clear")

    database.package_clear("package", repository_id)
    build_queue_mock.assert_called_once_with("package", repository_id)
    patches_mock.assert_called_once_with("package", None)
    logs_mock.assert_called_once_with("package", None, repository_id)
    changes_mock.assert_called_once_with("package", repository_id)
    dependencies_mock.assert_called_once_with("package", repository_id)
    package_mock.assert_called_once_with("package", repository_id)
    tree_clear_mock.assert_called_once_with("package")
