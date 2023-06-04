import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture
from unittest.mock import AsyncMock

from ahriman.models.user_access import UserAccess
from ahriman.web.views.service.add import AddView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await AddView.get_permission(request) == UserAccess.Full


async def test_post(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call post request correctly
    """
    add_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_add")
    user_mock = AsyncMock()
    user_mock.return_value = "username"
    mocker.patch("ahriman.web.views.base.BaseView.username", side_effect=user_mock)
    request_schema = pytest.helpers.schema_request(AddView.post)

    payload = {"packages": ["ahriman"]}
    assert not request_schema.validate(payload)
    response = await client.post("/api/v1/service/add", json=payload)
    assert response.ok
    add_mock.assert_called_once_with(["ahriman"], "username", now=True)


async def test_post_empty(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call raise 400 on empty request
    """
    add_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_add")
    response_schema = pytest.helpers.schema_response(AddView.post, code=400)

    response = await client.post("/api/v1/service/add", json={"packages": [""]})
    assert response.status == 400
    assert not response_schema.validate(await response.json())
    add_mock.assert_not_called()

    response = await client.post("/api/v1/service/add", json={"packages": []})
    assert response.status == 400
    assert not response_schema.validate(await response.json())
    add_mock.assert_not_called()

    response = await client.post("/api/v1/service/add", json={})
    assert response.status == 400
    assert not response_schema.validate(await response.json())
    add_mock.assert_not_called()
