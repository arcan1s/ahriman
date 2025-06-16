import pytest

from aiohttp.test_utils import TestClient
from aiohttp.web import Response
from pytest_mock import MockerFixture

from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.status.metrics import MetricsView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await MetricsView.get_permission(request) == UserAccess.Unauthorized


def test_routes() -> None:
    """
    must return correct routes
    """
    assert MetricsView.ROUTES == ["/api/v1/metrics"]


async def test_get(client: TestClient, mocker: MockerFixture) -> None:
    """
    must return service metrics
    """
    metrics_mock = mocker.patch("ahriman.web.views.v1.status.metrics.metrics", return_value=Response())

    response = await client.get("/api/v1/metrics")
    assert response.ok
    metrics_mock.assert_called_once_with(pytest.helpers.anyvar(int))
