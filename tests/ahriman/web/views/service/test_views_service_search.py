import aur
import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.user_access import UserAccess
from ahriman.web.views.service.search import SearchView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET", "HEAD"):
        request = pytest.helpers.request("", "", method)
        assert await SearchView.get_permission(request) == UserAccess.Read


async def test_get(client: TestClient, aur_package_ahriman: aur.Package, mocker: MockerFixture) -> None:
    """
    must call get request correctly
    """
    mocker.patch("ahriman.web.views.service.search.aur_search", return_value=[aur_package_ahriman])
    response = await client.get("/service-api/v1/search", params={"for": "ahriman"})

    assert response.ok
    assert await response.json() == [{"package": aur_package_ahriman.package_base,
                                      "description": aur_package_ahriman.description}]


async def test_get_exception(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise 400 on empty search string
    """
    search_mock = mocker.patch("ahriman.web.views.service.search.aur_search", return_value=[])
    response = await client.get("/service-api/v1/search")

    assert response.status == 404
    search_mock.assert_called_once_with()


async def test_get_join(client: TestClient, mocker: MockerFixture) -> None:
    """
    must join search args with space
    """
    search_mock = mocker.patch("ahriman.web.views.service.search.aur_search")
    response = await client.get("/service-api/v1/search", params=[("for", "ahriman"), ("for", "maybe")])

    assert response.ok
    search_mock.assert_called_once_with("ahriman", "maybe")
