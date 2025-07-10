import pytest

from pytest_mock import MockerFixture
from sqlite3 import Connection
from unittest.mock import call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.core.database.migrations.m011_repository_name import migrate_data, migrate_package_repository, steps


def test_migration_repository_name() -> None:
    """
    migration must not be empty
    """
    assert steps


def test_migrate_data(connection: Connection, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must perform data migration
    """
    repository_mock = mocker.patch("ahriman.core.database.migrations.m011_repository_name.migrate_package_repository")
    migrate_data(connection, configuration)
    repository_mock.assert_called_once_with(connection, configuration)


def test_migrate_package_repository(connection: Connection, configuration: Configuration) -> None:
    """
    must correctly set repository and architecture
    """
    migrate_package_repository(connection, configuration)

    connection.execute.assert_has_calls([
        MockCall(pytest.helpers.anyvar(str, strict=True), {"repository": configuration.repository_id.id}),
        MockCall(pytest.helpers.anyvar(str, strict=True), {"repository": configuration.repository_id.id}),
        MockCall(pytest.helpers.anyvar(str, strict=True), {"repository": configuration.repository_id.id}),
        MockCall(pytest.helpers.anyvar(str, strict=True), {"repository": configuration.repository_id.id}),
        MockCall(pytest.helpers.anyvar(str, strict=True), {"repository": configuration.repository_id.id}),
    ])
