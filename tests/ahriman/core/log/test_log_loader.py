import logging
import pytest
import sys

from logging.config import fileConfig
from pytest_mock import MockerFixture
from systemd.journal import JournalHandler

from ahriman.core.configuration import Configuration
from ahriman.core.log.log_loader import LogLoader
from ahriman.models.log_handler import LogHandler


def test_handler() -> None:
    """
    must extract journald handler if available
    """
    assert LogLoader.handler(None) == LogHandler.Journald


def test_handler_selected() -> None:
    """
    must return selected log handler
    """
    assert LogLoader.handler(LogHandler.Console) == LogHandler.Console


def test_handler_syslog(mocker: MockerFixture) -> None:
    """
    must return syslog handler if no journal is available
    """
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch.dict(sys.modules, {"systemd.journal": None})
    assert LogLoader.handler(None) == LogHandler.Syslog


def test_handler_console(mocker: MockerFixture) -> None:
    """
    must return console handler if no journal is available and no log device was found
    """
    mocker.patch("pathlib.Path.exists", return_value=False)
    mocker.patch.dict(sys.modules, {"systemd.journal": None})
    assert LogLoader.handler(None) == LogHandler.Console


def test_load(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must load logging
    """
    logging_mock = mocker.patch("ahriman.core.log.log_loader.fileConfig", side_effect=fileConfig)
    http_log_mock = mocker.patch("ahriman.core.log.http_log_handler.HttpLogHandler.load")

    _, repository_id = configuration.check_loaded()
    LogLoader.load(repository_id, configuration, LogHandler.Journald, quiet=False, report=False)
    logging_mock.assert_called_once_with(pytest.helpers.anyvar(int), disable_existing_loggers=True)
    http_log_mock.assert_called_once_with(repository_id, configuration, report=False)
    assert all(isinstance(handler, JournalHandler) for handler in logging.getLogger().handlers)


def test_load_fallback(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must fall back to stderr without errors
    """
    mocker.patch("ahriman.core.log.log_loader.fileConfig", side_effect=PermissionError())
    _, repository_id = configuration.check_loaded()
    LogLoader.load(repository_id, configuration, LogHandler.Journald, quiet=False, report=False)


def test_load_quiet(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must disable logging in case if quiet flag set
    """
    disable_mock = mocker.patch("logging.disable")

    _, repository_id = configuration.check_loaded()
    LogLoader.load(repository_id, configuration, LogHandler.Journald, quiet=True, report=False)
    disable_mock.assert_called_once_with(logging.WARNING)
