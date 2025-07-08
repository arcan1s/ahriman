import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.core.formatters.configuration_printer import ConfigurationPrinter
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.service.config import ConfigView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await ConfigView.get_permission(request) == UserAccess.Full
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await ConfigView.get_permission(request) == UserAccess.Full


def test_routes() -> None:
    """
    must return correct routes
    """
    assert ConfigView.ROUTES == ["/api/v1/service/config"]


async def test_get(client: TestClient) -> None:
    """
    must get web configuration
    """
    response_schema = pytest.helpers.schema_response(ConfigView.get)

    response = await client.get("/api/v1/service/config")
    assert response.status == 200
    json = await response.json()
    assert json  # check that it is not empty
    assert not response_schema.validate(json)

    # check that there are no keys which have to be hidden
    assert not any(value["key"] in ConfigurationPrinter.HIDE_KEYS for value in json)


async def test_post(client: TestClient, mocker: MockerFixture) -> None:
    """
    must update package changes
    """
    reload_mock = mocker.patch("ahriman.core.configuration.Configuration.reload")

    response = await client.post("/api/v1/service/config")
    assert response.status == 204
    reload_mock.assert_called_once_with()
