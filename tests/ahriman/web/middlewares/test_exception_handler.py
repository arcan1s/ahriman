import json
import logging
import pytest

from aiohttp.web import HTTPBadRequest, HTTPInternalServerError, HTTPMethodNotAllowed, HTTPNoContent, HTTPUnauthorized
from pytest_mock import MockerFixture
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from ahriman.web.middlewares.exception_handler import _is_templated_unauthorized, exception_handler


def _extract_body(response: Any) -> Any:
    """
    extract json body from given object

    Args:
        response(Any): response (any actually) object

    Returns:
        Any: body key from the object converted to json
    """
    return json.loads(getattr(response, "body"))


def test_is_templated_unauthorized() -> None:
    """
    must correct check if response should be rendered as template
    """
    response_mock = MagicMock()

    response_mock.path = "/api/v1/login"
    response_mock.headers.getall.return_value = ["*/*"]
    assert _is_templated_unauthorized(response_mock)

    response_mock.path = "/api/v1/login"
    response_mock.headers.getall.return_value = ["application/json"]
    assert not _is_templated_unauthorized(response_mock)

    response_mock.path = "/api/v1/logout"
    response_mock.headers.getall.return_value = ["*/*"]
    assert _is_templated_unauthorized(response_mock)

    response_mock.path = "/api/v1/logout"
    response_mock.headers.getall.return_value = ["application/json"]
    assert not _is_templated_unauthorized(response_mock)

    response_mock.path = "/api/v1/status"
    response_mock.headers.getall.return_value = ["*/*"]
    assert not _is_templated_unauthorized(response_mock)

    response_mock.path = "/api/v1/status"
    response_mock.headers.getall.return_value = ["application/json"]
    assert not _is_templated_unauthorized(response_mock)


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


async def test_exception_handler_unauthorized(mocker: MockerFixture) -> None:
    """
    must handle unauthorized exception as json response
    """
    request = pytest.helpers.request("", "", "")
    request_handler = AsyncMock(side_effect=HTTPUnauthorized())
    mocker.patch("ahriman.web.middlewares.exception_handler._is_templated_unauthorized", return_value=False)
    render_mock = mocker.patch("aiohttp_jinja2.render_template")

    handler = exception_handler(logging.getLogger())
    response = await handler(request, request_handler)
    assert _extract_body(response) == {"error": HTTPUnauthorized().reason}
    render_mock.assert_not_called()


async def test_exception_handler_unauthorized_templated(mocker: MockerFixture) -> None:
    """
    must handle unauthorized exception as json response
    """
    request = pytest.helpers.request("", "", "")
    request_handler = AsyncMock(side_effect=HTTPUnauthorized())
    mocker.patch("ahriman.web.middlewares.exception_handler._is_templated_unauthorized", return_value=True)
    render_mock = mocker.patch("aiohttp_jinja2.render_template")

    handler = exception_handler(logging.getLogger())
    await handler(request, request_handler)
    context = {"code": 401, "reason": "Unauthorized"}
    render_mock.assert_called_once_with("error.jinja2", request, context, status=HTTPUnauthorized.status_code)


async def test_exception_handler_options() -> None:
    """
    must handle OPTIONS request
    """
    request = pytest.helpers.request("", "", "OPTIONS")
    request_handler = AsyncMock(side_effect=HTTPMethodNotAllowed("OPTIONS", ["GET"]))

    handler = exception_handler(logging.getLogger())
    with pytest.raises(HTTPNoContent) as response:
        await handler(request, request_handler)
        assert response.headers["Allow"] == "GET"


async def test_exception_handler_head() -> None:
    """
    must handle missing HEAD requests
    """
    request = pytest.helpers.request("", "", "HEAD")
    request_handler = AsyncMock(side_effect=HTTPMethodNotAllowed("HEAD", ["HEAD,GET"]))

    handler = exception_handler(logging.getLogger())
    with pytest.raises(HTTPMethodNotAllowed) as response:
        await handler(request, request_handler)
        assert response.headers["Allow"] == "GET"


async def test_exception_handler_method_not_allowed() -> None:
    """
    must handle not allowed methodss
    """
    request = pytest.helpers.request("", "", "POST")
    request_handler = AsyncMock(side_effect=HTTPMethodNotAllowed("POST", ["GET"]))

    handler = exception_handler(logging.getLogger())
    with pytest.raises(HTTPMethodNotAllowed):
        await handler(request, request_handler)


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
