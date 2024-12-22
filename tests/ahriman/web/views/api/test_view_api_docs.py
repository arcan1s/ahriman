import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.models.user_access import UserAccess
from ahriman.web.views.api.docs import DocsView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await DocsView.get_permission(request) == UserAccess.Unauthorized


def test_routes() -> None:
    """
    must return correct routes
    """
    assert DocsView.ROUTES == ["/api-docs"]


def test_routes_dynamic(configuration: Configuration) -> None:
    """
    must correctly return docs route
    """
    assert DocsView.ROUTES == DocsView.routes(configuration)


def test_routes_dynamic_not_found(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must disable docs route if no apispec package found
    """
    mocker.patch("ahriman.web.views.api.docs.aiohttp_apispec", None)
    assert DocsView.routes(configuration) == []


async def test_get(client: TestClient) -> None:
    """
    must generate api-docs correctly
    """
    response = await client.get("/api-docs")
    assert response.ok
    assert await response.text()
