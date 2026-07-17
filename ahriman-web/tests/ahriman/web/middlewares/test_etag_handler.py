import hashlib
import pytest

from aiohttp import ETag
from aiohttp.web import HTTPNotModified, Response, StreamResponse
from unittest.mock import AsyncMock

from ahriman.web.middlewares.etag_handler import etag_handler


async def test_etag_handler() -> None:
    """
    must set ETag header on GET responses
    """
    request = pytest.helpers.request("", "", "GET")
    request.if_none_match = None
    request_handler = AsyncMock(return_value=Response(body=b"hello"))

    handler = etag_handler()
    result = await handler(request, request_handler)
    assert result.etag is not None


async def test_etag_handler_not_modified() -> None:
    """
    must raise NotModified when ETag matches If-None-Match
    """
    body = b"hello"
    request = pytest.helpers.request("", "", "GET")
    request.if_none_match = (ETag(value=hashlib.md5(body, usedforsecurity=False).hexdigest()),)
    request_handler = AsyncMock(return_value=Response(body=body))

    handler = etag_handler()
    with pytest.raises(HTTPNotModified):
        await handler(request, request_handler)


async def test_etag_handler_no_match() -> None:
    """
    must return full response when ETag does not match If-None-Match
    """
    request = pytest.helpers.request("", "", "GET")
    request.if_none_match = (ETag(value="outdated"),)
    request_handler = AsyncMock(return_value=Response(body=b"hello"))

    handler = etag_handler()
    result = await handler(request, request_handler)
    assert result.status == 200
    assert result.etag is not None


async def test_etag_handler_skip_post() -> None:
    """
    must skip ETag for non-GET/HEAD methods
    """
    request = pytest.helpers.request("", "", "POST")
    request_handler = AsyncMock(return_value=Response(body=b"hello"))

    handler = etag_handler()
    result = await handler(request, request_handler)
    assert result.etag is None


async def test_etag_handler_skip_no_body() -> None:
    """
    must skip ETag for responses without body
    """
    request = pytest.helpers.request("", "", "GET")
    request_handler = AsyncMock(return_value=Response())

    handler = etag_handler()
    result = await handler(request, request_handler)
    assert result.etag is None


async def test_etag_handler_skip_stream() -> None:
    """
    must skip ETag for streaming responses
    """
    request = pytest.helpers.request("", "", "GET")
    request_handler = AsyncMock(return_value=StreamResponse())

    handler = etag_handler()
    result = await handler(request, request_handler)
    assert "ETag" not in result.headers
