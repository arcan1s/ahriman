import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.user_access import UserAccess
from ahriman.web.views.service.request import RequestView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await RequestView.get_permission(request) == UserAccess.Reporter


async def test_post(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call post request correctly
    """
    add_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_add")
    request_schema = pytest.helpers.schema_request(RequestView.post)

    payload = {"packages": ["ahriman"]}
    assert not request_schema.validate(payload)
    response = await client.post("/api/v1/service/request", json=payload)
    assert response.ok
    add_mock.assert_called_once_with(["ahriman"], now=False)


async def test_post_exception(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise exception on missing packages payload
    """
    add_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_add")
    response_schema = pytest.helpers.schema_response(RequestView.post, code=400)

    response = await client.post("/api/v1/service/request")
    assert response.status == 400
    assert not response_schema.validate(await response.json())
    add_mock.assert_not_called()
