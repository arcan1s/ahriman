import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.aur_package import AURPackage
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.service.search import SearchView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await SearchView.get_permission(request) == UserAccess.Reporter


def test_routes() -> None:
    """
    must return correct routes
    """
    assert SearchView.ROUTES == ["/api/v1/service/search"]


async def test_get(client: TestClient, aur_package_ahriman: AURPackage, mocker: MockerFixture) -> None:
    """
    must call get request correctly
    """
    mocker.patch("ahriman.core.alpm.remote.AUR.multisearch", return_value=[aur_package_ahriman])
    request_schema = pytest.helpers.schema_request(SearchView.get, location="querystring")
    response_schema = pytest.helpers.schema_response(SearchView.get)

    payload = {"for": ["ahriman"]}
    assert not request_schema.validate(payload)
    response = await client.get("/api/v1/service/search", params=payload)
    assert response.ok
    assert await response.json() == [{"package": aur_package_ahriman.package_base,
                                      "description": aur_package_ahriman.description}]
    assert not response_schema.validate(await response.json(), many=True)


async def test_get_exception(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise 400 on empty search string
    """
    search_mock = mocker.patch("ahriman.core.alpm.remote.AUR.multisearch")
    response_schema = pytest.helpers.schema_response(SearchView.get, code=400)

    response = await client.get("/api/v1/service/search")
    assert response.status == 400
    assert not response_schema.validate(await response.json())
    search_mock.assert_not_called()


async def test_get_empty(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise 404 on empty search result
    """
    mocker.patch("ahriman.core.alpm.remote.AUR.multisearch", return_value=[])
    response_schema = pytest.helpers.schema_response(SearchView.get, code=404)

    response = await client.get("/api/v1/service/search", params={"for": ["ahriman"]})
    assert response.status == 404
    assert not response_schema.validate(await response.json())


async def test_get_join(client: TestClient, mocker: MockerFixture) -> None:
    """
    must join search args with space
    """
    search_mock = mocker.patch("ahriman.core.alpm.remote.AUR.multisearch")
    request_schema = pytest.helpers.schema_request(SearchView.get, location="querystring")

    payload = {"for": ["ahriman", "maybe"]}
    assert not request_schema.validate(payload)
    response = await client.get("/api/v1/service/search", params=payload)
    assert response.ok
    search_mock.assert_called_once_with("ahriman", "maybe")
