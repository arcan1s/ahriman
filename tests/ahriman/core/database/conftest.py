import pytest

from sqlite3 import Connection
from unittest.mock import MagicMock


@pytest.fixture
def connection() -> Connection:
    """
    mock object for sqlite3 connection

    Returns:
      Connection: sqlite3 connection test instance
    """
    return MagicMock()
