import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.aur_package import AURPackage
from ahriman.models.user_access import UserAccess
from ahriman.web.schemas.aur_package_schema import AURPackageSchema
from ahriman.web.schemas.error_schema import ErrorSchema
from ahriman.web.schemas.search_schema import SearchSchema
from ahriman.web.views.service.search import SearchView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await SearchView.get_permission(request) == UserAccess.Reporter


async def test_get(client: TestClient, aur_package_ahriman: AURPackage, mocker: MockerFixture) -> None:
    """
    must call get request correctly
    """
    mocker.patch("ahriman.core.alpm.remote.AUR.multisearch", return_value=[aur_package_ahriman])
    request_schema = SearchSchema()
    response_schema = AURPackageSchema()

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
    response_schema = ErrorSchema()

    response = await client.get("/api/v1/service/search")
    assert response.status == 400
    assert not response_schema.validate(await response.json())
    search_mock.assert_not_called()


async def test_get_empty(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise 404 on empty search result
    """
    mocker.patch("ahriman.core.alpm.remote.AUR.multisearch", return_value=[])
    response_schema = ErrorSchema()

    response = await client.get("/api/v1/service/search", params={"for": ["ahriman"]})
    assert response.status == 404
    assert not response_schema.validate(await response.json())


async def test_get_join(client: TestClient, mocker: MockerFixture) -> None:
    """
    must join search args with space
    """
    search_mock = mocker.patch("ahriman.core.alpm.remote.AUR.multisearch")
    request_schema = SearchSchema()

    payload = {"for": ["ahriman", "maybe"]}
    assert not request_schema.validate(payload)
    response = await client.get("/api/v1/service/search", params=payload)
    assert response.ok
    search_mock.assert_called_once_with("ahriman", "maybe", pacman=pytest.helpers.anyvar(int))
