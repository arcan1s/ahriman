import logging

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.log import Log


def test_load(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must load logging
    """
    logging_mock = mocker.patch("ahriman.core.log.log.fileConfig")
    http_log_mock = mocker.patch("ahriman.core.log.http_log_handler.HttpLogHandler.load")

    Log.load(configuration, quiet=False, report=False)
    logging_mock.assert_called_once_with(configuration.logging_path)
    http_log_mock.assert_called_once_with(configuration, report=False)


def test_load_fallback(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must fallback to stderr without errors
    """
    mocker.patch("ahriman.core.log.log.fileConfig", side_effect=PermissionError())
    Log.load(configuration, quiet=False, report=False)


def test_load_quiet(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must disable logging in case if quiet flag set
    """
    disable_mock = mocker.patch("logging.disable")
    Log.load(configuration, quiet=True, report=False)
    disable_mock.assert_called_once_with(logging.WARNING)
