import logging
import pytest

from pytest_mock import MockerFixture

from ahriman.core.alpm.repo import Repo
from ahriman.core.database import SQLite
from ahriman.models.package import Package


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


def test_package_logger_set_reset(database: SQLite) -> None:
    """
    must set and reset package base attribute
    """
    package_base = "package base"

    database._package_logger_set(package_base)
    record = logging.makeLogRecord({})
    assert record.package_base == package_base

    database._package_logger_reset()
    record = logging.makeLogRecord({})
    with pytest.raises(AttributeError):
        record.package_base


def test_in_package_context(database: SQLite, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must set package log context
    """
    set_mock = mocker.patch("ahriman.core.log.LazyLogging._package_logger_set")
    reset_mock = mocker.patch("ahriman.core.log.LazyLogging._package_logger_reset")

    with database.in_package_context(package_ahriman.base):
        pass

    set_mock.assert_called_once_with(package_ahriman.base)
    reset_mock.assert_called_once_with()


def test_in_package_context_failed(database: SQLite, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must reset package context even if exception occurs
    """
    mocker.patch("ahriman.core.log.LazyLogging._package_logger_set")
    reset_mock = mocker.patch("ahriman.core.log.LazyLogging._package_logger_reset")

    with pytest.raises(Exception):
        with database.in_package_context(package_ahriman.base):
            raise Exception()

    reset_mock.assert_called_once_with()
