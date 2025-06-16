import pytest
import sqlite3

from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.database import SQLite


def test_logger_name(database: SQLite) -> None:
    """
    must return correct logger name
    """
    assert database.logger_name == "sql"


def test_factory(database: SQLite) -> None:
    """
    must convert response to dictionary
    """
    result = database.with_connection(lambda conn: conn.execute("select 1 as result").fetchone())
    assert isinstance(result, dict)
    assert result["result"] == 1


def test_with_connection(database: SQLite, mocker: MockerFixture) -> None:
    """
    must run query inside connection and close it at the end
    """
    connection_mock = MagicMock()
    connect_mock = mocker.patch("sqlite3.connect", return_value=connection_mock)

    database.with_connection(lambda conn: conn.execute("select 1"))
    connect_mock.assert_called_once_with(database.path, detect_types=sqlite3.PARSE_DECLTYPES)
    connection_mock.set_trace_callback.assert_called_once_with(database.logger.debug)
    connection_mock.commit.assert_not_called()
    connection_mock.close.assert_called_once_with()


def test_with_connection_close(database: SQLite, mocker: MockerFixture) -> None:
    """
    must close connection on errors
    """
    connection_mock = MagicMock()
    connection_mock.commit.side_effect = Exception
    mocker.patch("sqlite3.connect", return_value=connection_mock)

    with pytest.raises(Exception):
        database.with_connection(lambda conn: conn.execute("select 1"), commit=True)
    connection_mock.close.assert_called_once_with()


def test_with_connection_with_commit(database: SQLite, mocker: MockerFixture) -> None:
    """
    must run query inside connection and commit after
    """
    connection_mock = MagicMock()
    connection_mock.commit.return_value = 42
    mocker.patch("sqlite3.connect", return_value=connection_mock)

    database.with_connection(lambda conn: conn.execute("select 1"), commit=True)
    connection_mock.commit.assert_called_once_with()
