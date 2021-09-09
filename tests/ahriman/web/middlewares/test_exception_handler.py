import logging
import pytest

from aiohttp.web_exceptions import HTTPBadRequest
from pytest_mock import MockerFixture
from unittest.mock import AsyncMock

from ahriman.web.middlewares.exception_handler import exception_handler


async def test_exception_handler(mocker: MockerFixture) -> None:
    """
    must pass success response
    """
    request = pytest.helpers.request("", "", "")
    request_handler = AsyncMock()
    logging_mock = mocker.patch("logging.Logger.exception")

    handler = exception_handler(logging.getLogger())
    await handler(request, request_handler)
    logging_mock.assert_not_called()


async def test_exception_handler_client_error(mocker: MockerFixture) -> None:
    """
    must pass client exception
    """
    request = pytest.helpers.request("", "", "")
    request_handler = AsyncMock(side_effect=HTTPBadRequest())
    logging_mock = mocker.patch("logging.Logger.exception")

    handler = exception_handler(logging.getLogger())
    with pytest.raises(HTTPBadRequest):
        await handler(request, request_handler)
    logging_mock.assert_not_called()


async def test_exception_handler_server_error(mocker: MockerFixture) -> None:
    """
    must log server exception and re-raise it
    """
    request = pytest.helpers.request("", "", "")
    request_handler = AsyncMock(side_effect=Exception())
    logging_mock = mocker.patch("logging.Logger.exception")

    handler = exception_handler(logging.getLogger())
    with pytest.raises(Exception):
        await handler(request, request_handler)
    logging_mock.assert_called_once()
