import pytest

from sqlite3 import Connection

from ahriman.core.database.migrations import Migrations


@pytest.fixture
def migrations(connection: Connection) -> Migrations:
    """
    fixture for migrations object
    :param connection: sqlite connection fixture
    :return: migrations test instance
    """
    return Migrations(connection)
