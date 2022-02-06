import pytest

from aiohttp.test_utils import TestClient

from ahriman.models.user_access import UserAccess
from ahriman.web.views.index import IndexView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET", "HEAD"):
        request = pytest.helpers.request("", "", method)
        assert await IndexView.get_permission(request) == UserAccess.Safe


async def test_get(client_with_auth: TestClient) -> None:
    """
    must generate status page correctly (/)
    """
    response = await client_with_auth.get("/")
    assert response.ok
    assert await response.text()


async def test_get_index(client_with_auth: TestClient) -> None:
    """
    must generate status page correctly (/index.html)
    """
    response = await client_with_auth.get("/index.html")
    assert response.ok
    assert await response.text()


async def test_get_without_auth(client: TestClient) -> None:
    """
    must use dummy authorized_userid function in case if no security library installed
    """
    response = await client.get("/")
    assert response.ok
    assert await response.text()


async def test_get_static(client: TestClient) -> None:
    """
    must return static files
    """
    response = await client.get("/static/favicon.ico")
    assert response.ok


async def test_get_static_with_auth(client_with_auth: TestClient) -> None:
    """
    must return static files
    """
    response = await client_with_auth.get("/static/favicon.ico")
    assert response.ok
