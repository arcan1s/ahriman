import sqlite3

from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.database import SQLite


def test_factory(database: SQLite) -> None:
    """
    must convert response to dictionary
    """
    result = database.with_connection(lambda conn: conn.execute("select 1 as result").fetchone())
    assert isinstance(result, dict)
    assert result["result"] == 1


def test_with_connection(database: SQLite, mocker: MockerFixture) -> None:
    """
    must run query inside connection
    """
    connection_mock = MagicMock()
    connect_mock = mocker.patch("sqlite3.connect", return_value=connection_mock)

    database.with_connection(lambda conn: conn.execute("select 1"))
    connect_mock.assert_called_once_with(database.path, detect_types=sqlite3.PARSE_DECLTYPES)
    connection_mock.__enter__().commit.assert_not_called()


def test_with_connection_with_commit(database: SQLite, mocker: MockerFixture) -> None:
    """
    must run query inside connection and commit after
    """
    connection_mock = MagicMock()
    connection_mock.commit.return_value = 42
    mocker.patch("sqlite3.connect", return_value=connection_mock)

    database.with_connection(lambda conn: conn.execute("select 1"), commit=True)
    connection_mock.__enter__().commit.assert_called_once_with()
