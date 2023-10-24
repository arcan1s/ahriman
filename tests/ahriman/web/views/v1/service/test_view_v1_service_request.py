import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture
from unittest.mock import AsyncMock

from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.repository_id import RepositoryId
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.service.request import RequestView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await RequestView.get_permission(request) == UserAccess.Reporter


def test_routes() -> None:
    """
    must return correct routes
    """
    assert RequestView.ROUTES == ["/api/v1/service/request"]


async def test_post(client: TestClient, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must call post request correctly
    """
    add_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_add", return_value="abc")
    user_mock = AsyncMock()
    user_mock.return_value = "username"
    mocker.patch("ahriman.web.views.base.BaseView.username", side_effect=user_mock)
    request_schema = pytest.helpers.schema_request(RequestView.post)
    response_schema = pytest.helpers.schema_response(RequestView.post)

    payload = {"packages": ["ahriman"]}
    assert not request_schema.validate(payload)
    response = await client.post("/api/v1/service/request", json=payload)
    assert response.ok
    add_mock.assert_called_once_with(repository_id, ["ahriman"], "username", patches=[], now=False)

    json = await response.json()
    assert json["process_id"] == "abc"
    assert not response_schema.validate(json)


async def test_post_patches(client: TestClient, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must call post request with patches correctly
    """
    add_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_add", return_value="abc")
    user_mock = AsyncMock()
    user_mock.return_value = "username"
    mocker.patch("ahriman.web.views.base.BaseView.username", side_effect=user_mock)
    request_schema = pytest.helpers.schema_request(RequestView.post)

    payload = {
        "packages": ["ahriman"],
        "patches": [
            {
                "key": "k",
                "value": "v",
            },
            {
                "key": "k2",
            },
        ]
    }
    assert not request_schema.validate(payload)
    response = await client.post("/api/v1/service/request", json=payload)
    assert response.ok
    add_mock.assert_called_once_with(repository_id, ["ahriman"], "username",
                                     patches=[PkgbuildPatch("k", "v"), PkgbuildPatch("k2", "")], now=False)


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
