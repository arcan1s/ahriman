import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture
from unittest.mock import AsyncMock

from ahriman.models.repository_id import RepositoryId
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.service.update import UpdateView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await UpdateView.get_permission(request) == UserAccess.Full


def test_routes() -> None:
    """
    must return correct routes
    """
    assert UpdateView.ROUTES == ["/api/v1/service/update"]


async def test_post(client: TestClient, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must call post request correctly for alias
    """
    update_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_update", return_value="abc")
    user_mock = AsyncMock()
    user_mock.return_value = "username"
    mocker.patch("ahriman.web.views.base.BaseView.username", side_effect=user_mock)
    request_schema = pytest.helpers.schema_request(UpdateView.post)
    response_schema = pytest.helpers.schema_response(UpdateView.post)

    defaults = {
        "aur": True,
        "local": True,
        "manual": True,
    }

    for payload in (
            {},
            {"aur": False},
            {"local": False},
            {"manual": False},
    ):
        assert not request_schema.validate(payload)
        response = await client.post("/api/v1/service/update", json=payload)
        assert response.ok
        update_mock.assert_called_once_with(repository_id, "username", **(defaults | payload))
        update_mock.reset_mock()

        json = await response.json()
        assert json["process_id"] == "abc"
        assert not response_schema.validate(json)


async def test_post_empty(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call raise 400 on invalid request
    """
    mocker.patch("ahriman.web.views.base.BaseView.extract_data", side_effect=Exception())
    update_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_update")
    response_schema = pytest.helpers.schema_response(UpdateView.post, code=400)

    response = await client.post("/api/v1/service/update")
    assert response.status == 400
    assert not response_schema.validate(await response.json())
    update_mock.assert_not_called()
