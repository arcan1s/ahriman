import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.user_access import UserAccess
from ahriman.web.views.service.remove import RemoveView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await RemoveView.get_permission(request) == UserAccess.Full


async def test_post(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call post request correctly
    """
    remove_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_remove", return_value="abc")
    request_schema = pytest.helpers.schema_request(RemoveView.post)
    response_schema = pytest.helpers.schema_response(RemoveView.post)

    payload = {"packages": ["ahriman"]}
    assert not request_schema.validate(payload)
    response = await client.post("/api/v1/service/remove", json=payload)
    assert response.ok
    remove_mock.assert_called_once_with(["ahriman"])

    json = await response.json()
    assert json["process_id"] == "abc"
    assert not response_schema.validate(json)


async def test_post_exception(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise exception on missing packages payload
    """
    remove_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_remove")
    response_schema = pytest.helpers.schema_response(RemoveView.post, code=400)

    response = await client.post("/api/v1/service/remove")
    assert response.status == 400
    assert not response_schema.validate(await response.json())
    remove_mock.assert_not_called()
