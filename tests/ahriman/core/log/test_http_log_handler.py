import logging

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.log.http_log_handler import HttpLogHandler


def test_load(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must load handler
    """
    # because of test cases we need to reset handler list
    root = logging.getLogger()
    current_handler = next((handler for handler in root.handlers if isinstance(handler, HttpLogHandler)), None)
    root.removeHandler(current_handler)

    add_mock = mocker.patch("logging.Logger.addHandler")
    load_mock = mocker.patch("ahriman.core.status.client.Client.load")

    handler = HttpLogHandler.load(configuration, report=False)
    assert handler
    add_mock.assert_called_once_with(handler)
    load_mock.assert_called_once_with(configuration, report=False)


def test_load_exist(configuration: Configuration) -> None:
    """
    must not load handler if already set
    """
    handler = HttpLogHandler.load(configuration, report=False)
    new_handler = HttpLogHandler.load(configuration, report=False)
    assert handler is new_handler


def test_emit(configuration: Configuration, log_record: logging.LogRecord, mocker: MockerFixture) -> None:
    """
    must emit log record to reporter
    """
    log_mock = mocker.patch("ahriman.core.status.client.Client.logs")
    handler = HttpLogHandler(configuration, report=False)

    handler.emit(log_record)
    log_mock.assert_called_once_with(log_record)


def test_emit_failed(configuration: Configuration, log_record: logging.LogRecord, mocker: MockerFixture) -> None:
    """
    must call handle error on exception
    """
    mocker.patch("ahriman.core.status.client.Client.logs", side_effect=Exception())
    handle_error_mock = mocker.patch("logging.Handler.handleError")
    handler = HttpLogHandler(configuration, report=False)

    handler.emit(log_record)
    handle_error_mock.assert_called_once_with(log_record)
