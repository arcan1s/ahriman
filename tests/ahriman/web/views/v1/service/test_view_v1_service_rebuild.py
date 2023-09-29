import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture
from unittest.mock import AsyncMock

from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.service.rebuild import RebuildView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await RebuildView.get_permission(request) == UserAccess.Full


def test_routes() -> None:
    """
    must return correct routes
    """
    assert RebuildView.ROUTES == ["/api/v1/service/rebuild"]


async def test_post(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call post request correctly
    """
    rebuild_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_rebuild", return_value="abc")
    user_mock = AsyncMock()
    user_mock.return_value = "username"
    mocker.patch("ahriman.web.views.base.BaseView.username", side_effect=user_mock)
    request_schema = pytest.helpers.schema_request(RebuildView.post)
    response_schema = pytest.helpers.schema_response(RebuildView.post)

    payload = {"packages": ["python", "ahriman"]}
    assert not request_schema.validate(payload)
    response = await client.post("/api/v1/service/rebuild", json=payload)
    assert response.ok
    rebuild_mock.assert_called_once_with("python", "username")

    json = await response.json()
    assert json["process_id"] == "abc"
    assert not response_schema.validate(json)


async def test_post_exception(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise exception on missing packages payload
    """
    rebuild_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_rebuild")
    response_schema = pytest.helpers.schema_response(RebuildView.post, code=400)

    response = await client.post("/api/v1/service/rebuild")
    assert response.status == 400
    assert not response_schema.validate(await response.json())
    rebuild_mock.assert_not_called()
