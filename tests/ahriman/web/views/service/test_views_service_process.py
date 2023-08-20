import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.user_access import UserAccess
from ahriman.web.views.service.process import ProcessView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await ProcessView.get_permission(request) == UserAccess.Reporter


async def test_get(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call post request correctly
    """
    process = "abc"
    process_mock = mocker.patch("ahriman.core.spawn.Spawn.has_process", return_value=True)
    response_schema = pytest.helpers.schema_response(ProcessView.get)

    response = await client.get(f"/api/v1/service/process/{process}")
    assert response.ok
    process_mock.assert_called_once_with(process)

    json = await response.json()
    assert json["is_alive"]
    assert not response_schema.validate(json)


async def test_get_empty(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call raise 404 on unknown process
    """
    process = "abc"
    mocker.patch("ahriman.core.spawn.Spawn.has_process", return_value=False)
    response_schema = pytest.helpers.schema_response(ProcessView.get, code=404)

    response = await client.get(f"/api/v1/service/process/{process}")
    assert response.status == 404
    assert not response_schema.validate(await response.json())
