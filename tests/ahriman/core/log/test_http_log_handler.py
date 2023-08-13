import logging

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.log.http_log_handler import HttpLogHandler
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


def test_emit(configuration: Configuration, log_record: logging.LogRecord, package_ahriman: Package,
              mocker: MockerFixture) -> None:
    """
    must emit log record to reporter
    """
    log_record.package_base = package_ahriman.base
    log_mock = mocker.patch("ahriman.core.status.client.Client.package_logs")

    handler = HttpLogHandler(configuration, report=False)

    handler.emit(log_record)
    log_mock.assert_called_once_with(package_ahriman.base, log_record)


def test_emit_skip(configuration: Configuration, log_record: logging.LogRecord, mocker: MockerFixture) -> None:
    """
    must skip log record posting if no package base set
    """
    log_mock = mocker.patch("ahriman.core.status.client.Client.package_logs")
    handler = HttpLogHandler(configuration, report=False)

    handler.emit(log_record)
    log_mock.assert_not_called()
