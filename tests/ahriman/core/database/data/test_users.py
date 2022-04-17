import pytest

from sqlite3 import Connection
from unittest import mock

from ahriman.core.configuration import Configuration
from ahriman.core.database.data import migrate_users_data


def test_migrate_users_data(connection: Connection, configuration: Configuration) -> None:
    """
    must users to database
    """
    configuration.set_option("auth:read", "user1", "password1")
    configuration.set_option("auth:write", "user2", "password2")

    migrate_users_data(connection, configuration)
    connection.execute.assert_has_calls([
        mock.call(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int)),
        mock.call(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int)),
    ])
