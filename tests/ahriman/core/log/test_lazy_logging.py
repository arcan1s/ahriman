import logging
import pytest

from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

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


def test_package_logger_set_reset(database: SQLite) -> None:
    """
    must set and reset package base attribute
    """
    log_record_id = LogRecordId("base", "version")

    database._package_logger_set(log_record_id.package_base, log_record_id.version)
    record = logging.makeLogRecord({})
    assert record.package_id == log_record_id

    database._package_logger_reset()
    record = logging.makeLogRecord({})
    with pytest.raises(AttributeError):
        assert record.package_id


def test_in_package_context(database: SQLite, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must set package log context
    """
    set_mock = mocker.patch("ahriman.core.log.LazyLogging._package_logger_set")
    reset_mock = mocker.patch("ahriman.core.log.LazyLogging._package_logger_reset")

    with database.in_package_context(package_ahriman.base, package_ahriman.version):
        pass

    set_mock.assert_called_once_with(package_ahriman.base, package_ahriman.version)
    reset_mock.assert_called_once_with()


def test_in_package_context_empty_version(database: SQLite, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must set package log context with empty version
    """
    set_mock = mocker.patch("ahriman.core.log.LazyLogging._package_logger_set")
    reset_mock = mocker.patch("ahriman.core.log.LazyLogging._package_logger_reset")

    with database.in_package_context(package_ahriman.base, None):
        pass

    set_mock.assert_called_once_with(package_ahriman.base, None)
    reset_mock.assert_called_once_with()


def test_in_package_context_failed(database: SQLite, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must reset package context even if exception occurs
    """
    mocker.patch("ahriman.core.log.LazyLogging._package_logger_set")
    reset_mock = mocker.patch("ahriman.core.log.LazyLogging._package_logger_reset")

    with pytest.raises(ValueError):
        with database.in_package_context(package_ahriman.base, ""):
            raise ValueError()

    reset_mock.assert_called_once_with()
