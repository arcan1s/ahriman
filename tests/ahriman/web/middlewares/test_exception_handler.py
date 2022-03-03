import json
import logging
import pytest

from aiohttp.web_exceptions import HTTPBadRequest, HTTPInternalServerError, HTTPNoContent
from pytest_mock import MockerFixture
from typing import Any
from unittest.mock import AsyncMock

from ahriman.web.middlewares.exception_handler import exception_handler


def _extract_body(response: Any) -> Any:
    """
    extract json body from given object
    :param response: response (any actually) object
    :return: body key from the object converted to json
    """
    return json.loads(getattr(response, "body"))


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


async def test_exception_handler_success(mocker: MockerFixture) -> None:
    """
    must pass 2xx and 3xx codes
    """
    request = pytest.helpers.request("", "", "")
    request_handler = AsyncMock(side_effect=HTTPNoContent())
    logging_mock = mocker.patch("logging.Logger.exception")

    handler = exception_handler(logging.getLogger())
    with pytest.raises(HTTPNoContent):
        await handler(request, request_handler)
    logging_mock.assert_not_called()


async def test_exception_handler_client_error(mocker: MockerFixture) -> None:
    """
    must handle client exception
    """
    request = pytest.helpers.request("", "", "")
    request_handler = AsyncMock(side_effect=HTTPBadRequest())
    logging_mock = mocker.patch("logging.Logger.exception")

    handler = exception_handler(logging.getLogger())
    response = await handler(request, request_handler)
    assert _extract_body(response) == {"error": HTTPBadRequest().reason}
    logging_mock.assert_not_called()


async def test_exception_handler_server_error(mocker: MockerFixture) -> None:
    """
    must handle server exception
    """
    request = pytest.helpers.request("", "", "")
    request_handler = AsyncMock(side_effect=HTTPInternalServerError())
    logging_mock = mocker.patch("logging.Logger.exception")

    handler = exception_handler(logging.getLogger())
    response = await handler(request, request_handler)
    assert _extract_body(response) == {"error": HTTPInternalServerError().reason}
    logging_mock.assert_called_once()  # we do not check logging arguments


async def test_exception_handler_unknown_error(mocker: MockerFixture) -> None:
    """
    must log server exception and re-raise it
    """
    request = pytest.helpers.request("", "", "")
    request_handler = AsyncMock(side_effect=Exception("An error"))
    logging_mock = mocker.patch("logging.Logger.exception")

    handler = exception_handler(logging.getLogger())
    response = await handler(request, request_handler)
    assert _extract_body(response) == {"error": "An error"}
    logging_mock.assert_called_once()  # we do not check logging arguments
