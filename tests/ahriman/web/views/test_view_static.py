import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

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


async def test_get_not_found(client_with_auth: TestClient, mocker: MockerFixture) -> None:
    """
    must raise not found if path is invalid
    """
    static_route = next(route for route in client_with_auth.app.router.routes() if route.handler == StaticView)
    mocker.patch.object(static_route.handler, "ROUTES", [])
    response = await client_with_auth.get("/favicon.ico", allow_redirects=False)
    assert response.status == 404
