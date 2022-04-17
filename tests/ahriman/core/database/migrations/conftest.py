import pytest

from sqlite3 import Connection

from ahriman.core.configuration import Configuration
from ahriman.core.database.migrations import Migrations


@pytest.fixture
def migrations(connection: Connection, configuration: Configuration) -> Migrations:
    """
    fixture for migrations object

    Args:
        connection(Connection): sqlite connection fixture
        configuration(Configuration): configuration fixture

    Returns:
        Migrations: migrations test instance
    """
    return Migrations(connection, configuration)
