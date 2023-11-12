import pytest

from aiohttp.test_utils import TestClient

from ahriman.models.user_access import UserAccess
from ahriman.web.views.static import StaticView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await StaticView.get_permission(request) == UserAccess.Unauthorized


def test_routes() -> None:
    """
    must return correct routes
    """
    assert StaticView.ROUTES == ["/favicon.ico"]


async def test_get(client_with_auth: TestClient) -> None:
    """
    must redirect favicon to static files
    """
    response = await client_with_auth.get("/favicon.ico", allow_redirects=False)
    assert response.status == 302
    assert response.headers["Location"] == "/static/favicon.ico"


async def test_get_not_found(client_with_auth: TestClient) -> None:
    """
    must raise not found if path is invalid
    """
    for route in client_with_auth.app.router.routes():
        if hasattr(route.handler, "ROUTES"):
            route.handler.ROUTES = []
    response = await client_with_auth.get("/favicon.ico", allow_redirects=False)
    assert response.status == 404
