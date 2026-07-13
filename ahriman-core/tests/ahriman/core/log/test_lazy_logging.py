import logging
import pytest

from ahriman.core.alpm.repo import Repo
from ahriman.core.build_tools.task import Task
from ahriman.core.database import SQLite
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package


def test_logger(database: SQLite, repo: Repo) -> None:
    """
    must set logger attribute
    """
    assert database.logger
    assert database.logger.name == "sql"

    assert repo.logger
    assert repo.logger.name == "ahriman.core.alpm.repo.Repo"


def test_logger_name(database: SQLite, repo: Repo, task_ahriman: Task) -> None:
    """
    must correctly generate logger name
    """
    assert database.logger_name == "sql"
    assert repo.logger_name == "ahriman.core.alpm.repo.Repo"
    assert task_ahriman.logger_name == "ahriman.core.build_tools.task.Task"


def test_in_context(database: SQLite) -> None:
    """
    must set and reset generic log context
    """
    with database.in_context("package_id", "42"):
        record = logging.makeLogRecord({})
        assert record.package_id == "42"

    record = logging.makeLogRecord({})
    assert not hasattr(record, "package_id")


def test_in_context_failed(database: SQLite) -> None:
    """
    must reset context even if exception occurs
    """
    with pytest.raises(ValueError):
        with database.in_context("package_id", "42"):
            raise ValueError()

    record = logging.makeLogRecord({})
    assert not hasattr(record, "package_id")


def test_in_package_context(database: SQLite, package_ahriman: Package) -> None:
    """
    must set package log context
    """
    with database.in_package_context(package_ahriman.base, package_ahriman.version):
        record = logging.makeLogRecord({})
        assert record.package_id == LogRecordId(package_ahriman.base, package_ahriman.version)

    record = logging.makeLogRecord({})
    assert not hasattr(record, "package_id")


def test_in_package_context_empty_version(database: SQLite, package_ahriman: Package) -> None:
    """
    must set package log context with empty version
    """
    with database.in_package_context(package_ahriman.base, None):
        record = logging.makeLogRecord({})
        assert record.package_id == LogRecordId(package_ahriman.base, "<unknown>")
