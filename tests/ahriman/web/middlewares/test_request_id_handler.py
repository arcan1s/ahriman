import logging
import pytest

from unittest.mock import AsyncMock, MagicMock
from typing import Any

from ahriman.web.middlewares.request_id_handler import request_id_handler


async def test_request_id_handler() -> None:
    """
    must use request id from request if available
    """
    request = pytest.helpers.request("", "", "")
    request.headers = MagicMock()
    request.headers.getone.return_value = "request_id"

    response = MagicMock()
    response.headers = {}

    async def check_handler(_: Any) -> MagicMock:
        record = logging.makeLogRecord({})
        assert record.request_id == "request_id"
        return response

    handler = request_id_handler()
    await handler(request, check_handler)
    assert response.headers["X-Request-ID"] == "request_id"


async def test_request_id_handler_generate() -> None:
    """
    must generate request id and set it in response header
    """
    request = pytest.helpers.request("", "", "")

    response = MagicMock()
    response.headers = {}
    request_handler = AsyncMock(return_value=response)

    handler = request_id_handler()
    await handler(request, request_handler)
    assert "X-Request-ID" in response.headers
