import pytest

from aiohttp.test_utils import TestClient
from aiohttp.web import Response
from pytest_mock import MockerFixture

import ahriman.web.middlewares.metrics_handler as metrics_handler

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
    # there is no response validation here, because it is free text, so we check call instead
    metrics_mock.assert_called_once_with(pytest.helpers.anyvar(int))


async def test_get_not_found(client: TestClient, mocker: MockerFixture) -> None:
    """
    must return 404 error if no module found
    """
    mocker.patch.object(metrics_handler, "aiohttp_openmetrics", None)
    response_schema = pytest.helpers.schema_response(MetricsView.get, code=404)

    response = await client.get("/api/v1/metrics")
    assert response.status == 404
    assert not response_schema.validate(await response.json())
