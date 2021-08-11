import logging
import pytest

from aiohttp.web_exceptions import HTTPBadRequest
from pytest_mock import MockerFixture
from typing import Any
from unittest.mock import AsyncMock

from ahriman.web.middlewares.exception_handler import exception_handler


async def test_exception_handler(aiohttp_request: Any, mocker: MockerFixture) -> None:
    """
    must pass success response
    """
    request_handler = AsyncMock()
    logging_mock = mocker.patch("logging.Logger.exception")

    handler = exception_handler(logging.getLogger())
    await handler(aiohttp_request, request_handler)
    logging_mock.assert_not_called()


async def test_exception_handler_client_error(aiohttp_request: Any, mocker: MockerFixture) -> None:
    """
    must pass client exception
    """
    request_handler = AsyncMock()
    request_handler.side_effect = HTTPBadRequest()
    logging_mock = mocker.patch("logging.Logger.exception")

    handler = exception_handler(logging.getLogger())
    with pytest.raises(HTTPBadRequest):
        await handler(aiohttp_request, request_handler)
    logging_mock.assert_not_called()


async def test_exception_handler_server_error(aiohttp_request: Any, mocker: MockerFixture) -> None:
    """
    must log server exception and re-raise it
    """
    request_handler = AsyncMock()
    request_handler.side_effect = Exception()
    logging_mock = mocker.patch("logging.Logger.exception")

    handler = exception_handler(logging.getLogger())
    with pytest.raises(Exception):
        await handler(aiohttp_request, request_handler)
    logging_mock.assert_called_once()
