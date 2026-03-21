import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture
from unittest.mock import AsyncMock

from ahriman.models.repository_id import RepositoryId
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.service.rollback import RollbackView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await RollbackView.get_permission(request) == UserAccess.Full


def test_routes() -> None:
    """
    must return correct routes
    """
    assert RollbackView.ROUTES == ["/api/v1/service/rollback"]


async def test_post(client: TestClient, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must call post request correctly
    """
    rollback_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_rollback", return_value="abc")
    user_mock = AsyncMock()
    user_mock.return_value = "username"
    mocker.patch("ahriman.web.views.base.BaseView.username", side_effect=user_mock)
    request_schema = pytest.helpers.schema_request(RollbackView.post)
    response_schema = pytest.helpers.schema_response(RollbackView.post)

    payload = {"package": "ahriman", "version": "version"}
    assert not request_schema.validate(payload)
    response = await client.post("/api/v1/service/rollback", json=payload)
    assert response.ok
    rollback_mock.assert_called_once_with(repository_id, "ahriman", "version", "username", hold=True)

    json = await response.json()
    assert json["process_id"] == "abc"
    assert not response_schema.validate(json)


async def test_post_empty(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call raise 400 on empty request
    """
    rollback_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_rollback")
    response_schema = pytest.helpers.schema_response(RollbackView.post, code=400)

    response = await client.post("/api/v1/service/rollback", json={"package": "", "version": "version"})
    assert response.status == 400
    assert not response_schema.validate(await response.json())
    rollback_mock.assert_not_called()

    response = await client.post("/api/v1/service/rollback", json={"package": "ahriman", "version": ""})
    assert response.status == 400
    assert not response_schema.validate(await response.json())
    rollback_mock.assert_not_called()

    response = await client.post("/api/v1/service/rollback", json={})
    assert response.status == 400
    assert not response_schema.validate(await response.json())
    rollback_mock.assert_not_called()
