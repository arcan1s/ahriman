import logging

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.log.http_log_handler import HttpLogHandler
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package


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

    _, repository_id = configuration.check_loaded()
    handler = HttpLogHandler.load(repository_id, configuration, report=False)
    assert handler
    add_mock.assert_called_once_with(handler)
    load_mock.assert_called_once_with(repository_id, configuration, report=False)


def test_load_exist(configuration: Configuration) -> None:
    """
    must not load handler if already set
    """
    _, repository_id = configuration.check_loaded()
    handler = HttpLogHandler.load(repository_id, configuration, report=False)
    new_handler = HttpLogHandler.load(repository_id, configuration, report=False)
    assert handler is new_handler


def test_emit(configuration: Configuration, log_record: logging.LogRecord, package_ahriman: Package,
              mocker: MockerFixture) -> None:
    """
    must emit log record to reporter
    """
    log_record_id = log_record.package_id = LogRecordId(package_ahriman.base, package_ahriman.version)
    log_mock = mocker.patch("ahriman.core.status.client.Client.package_logs")

    _, repository_id = configuration.check_loaded()
    handler = HttpLogHandler(repository_id, configuration, report=False, suppress_errors=False)

    handler.emit(log_record)
    log_mock.assert_called_once_with(log_record_id, log_record)


def test_emit_failed(configuration: Configuration, log_record: logging.LogRecord, package_ahriman: Package,
                     mocker: MockerFixture) -> None:
    """
    must call handle error on exception
    """
    log_record.package_id = LogRecordId(package_ahriman.base, package_ahriman.version)
    mocker.patch("ahriman.core.status.client.Client.package_logs", side_effect=Exception())
    handle_error_mock = mocker.patch("logging.Handler.handleError")
    _, repository_id = configuration.check_loaded()
    handler = HttpLogHandler(repository_id, configuration, report=False, suppress_errors=False)

    handler.emit(log_record)
    handle_error_mock.assert_called_once_with(log_record)


def test_emit_suppress_failed(configuration: Configuration, log_record: logging.LogRecord, package_ahriman: Package,
                              mocker: MockerFixture) -> None:
    """
    must not call handle error on exception if suppress flag is set
    """
    log_record.package_id = LogRecordId(package_ahriman.base, package_ahriman.version)
    mocker.patch("ahriman.core.status.client.Client.package_logs", side_effect=Exception())
    handle_error_mock = mocker.patch("logging.Handler.handleError")
    _, repository_id = configuration.check_loaded()
    handler = HttpLogHandler(repository_id, configuration, report=False, suppress_errors=True)

    handler.emit(log_record)
    handle_error_mock.assert_not_called()


def test_emit_skip(configuration: Configuration, log_record: logging.LogRecord, mocker: MockerFixture) -> None:
    """
    must skip log record posting if no package base set
    """
    log_mock = mocker.patch("ahriman.core.status.client.Client.package_logs")

    _, repository_id = configuration.check_loaded()
    handler = HttpLogHandler(repository_id, configuration, report=False, suppress_errors=False)

    handler.emit(log_record)
    log_mock.assert_not_called()
