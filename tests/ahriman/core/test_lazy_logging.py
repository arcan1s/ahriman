import pytest

from ahriman.core.alpm.repo import Repo
from ahriman.core.database import SQLite


def test_logger(database: SQLite) -> None:
    """
    must set logger attribute
    """
    assert database.logger
    assert database.logger.name == "ahriman.core.database.sqlite.SQLite"


def test_logger_attribute_error(database: SQLite) -> None:
    """
    must raise AttributeError in case if no attribute found
    """
    with pytest.raises(AttributeError):
        database.loggerrrr


def test_logger_name(database: SQLite, repo: Repo) -> None:
    """
    must correctly generate logger name
    """
    assert database.logger_name == "ahriman.core.database.sqlite.SQLite"
    assert repo.logger_name == "ahriman.core.alpm.repo.Repo"
