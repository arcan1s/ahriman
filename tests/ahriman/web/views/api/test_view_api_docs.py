import pytest

from aiohttp.test_utils import TestClient

from ahriman.models.user_access import UserAccess
from ahriman.web.views.api.docs import DocsView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await DocsView.get_permission(request) == UserAccess.Unauthorized


async def test_get(client: TestClient) -> None:
    """
    must generate api-docs correctly
    """
    response = await client.get("/api-docs")
    assert response.ok
    assert await response.text()
