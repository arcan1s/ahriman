from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.log.filtered_access_logger import FilteredAccessLogger


def test_is_logs_post() -> None:
    """
    must correctly define if request belongs to logs posting
    """
    request = MagicMock()

    request.method = "POST"
    request.path = "/api/v1/packages/ahriman/logs"
    assert FilteredAccessLogger.is_logs_post(request)

    request.method = "POST"
    request.path = "/api/v1/packages/linux-headers/logs"
    assert FilteredAccessLogger.is_logs_post(request)

    request.method = "POST"
    request.path = "/api/v1/packages/memtest86+/logs"
    assert FilteredAccessLogger.is_logs_post(request)

    request.method = "POST"
    request.path = "/api/v1/packages/memtest86%2B/logs"
    assert FilteredAccessLogger.is_logs_post(request)

    request.method = "POST"
    request.path = "/api/v1/packages/python2.7/logs"
    assert FilteredAccessLogger.is_logs_post(request)

    request.method = "GET"
    request.path = "/api/v1/packages/ahriman/logs"
    assert not FilteredAccessLogger.is_logs_post(request)

    request.method = "POST"
    request.path = "/api/v1/packages/ahriman"
    assert not FilteredAccessLogger.is_logs_post(request)

    request.method = "POST"
    request.path = "/api/v1/packages/ahriman/logs/random/path/after"
    assert not FilteredAccessLogger.is_logs_post(request)


def test_log(filtered_access_logger: FilteredAccessLogger, mocker: MockerFixture) -> None:
    """
    must emit log record
    """
    request_mock = MagicMock()
    response_mock = MagicMock()
    is_log_path_mock = mocker.patch("ahriman.core.log.filtered_access_logger.FilteredAccessLogger.is_logs_post",
                                    return_value=False)
    log_mock = mocker.patch("aiohttp.web_log.AccessLogger.log")

    filtered_access_logger.log(request_mock, response_mock, 0.001)
    is_log_path_mock.assert_called_once_with(request_mock)
    log_mock.assert_called_once_with(filtered_access_logger, request_mock, response_mock, 0.001)


def test_log_filter_logs(filtered_access_logger: FilteredAccessLogger, mocker: MockerFixture) -> None:
    """
    must skip log record in case if it is from logs posting
    """
    request_mock = MagicMock()
    response_mock = MagicMock()
    mocker.patch("ahriman.core.log.filtered_access_logger.FilteredAccessLogger.is_logs_post", return_value=True)
    log_mock = mocker.patch("aiohttp.web_log.AccessLogger.log")

    filtered_access_logger.log(request_mock, response_mock, 0.001)
    log_mock.assert_not_called()
