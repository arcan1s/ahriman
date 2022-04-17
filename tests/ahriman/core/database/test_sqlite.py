import pytest

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.database.sqlite import SQLite


def test_load(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must correctly load instance
    """
    init_mock = mocker.patch("ahriman.core.database.sqlite.SQLite.init")
    SQLite.load(configuration)
    init_mock.assert_called_once_with(configuration)


def test_init(database: SQLite, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run migrations on init
    """
    migrate_schema_mock = mocker.patch("ahriman.core.database.migrations.Migrations.migrate")
    database.init(configuration)
    migrate_schema_mock.assert_called_once_with(pytest.helpers.anyvar(int), configuration)
