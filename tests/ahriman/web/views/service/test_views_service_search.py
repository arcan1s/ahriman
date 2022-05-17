import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.aur_package import AURPackage
from ahriman.models.user_access import UserAccess
from ahriman.web.views.service.search import SearchView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET", "HEAD"):
        request = pytest.helpers.request("", "", method)
        assert await SearchView.get_permission(request) == UserAccess.Reporter


async def test_get(client: TestClient, aur_package_ahriman: AURPackage, mocker: MockerFixture) -> None:
    """
    must call get request correctly
    """
    mocker.patch("ahriman.core.alpm.remote.AUR.multisearch", return_value=[aur_package_ahriman])
    response = await client.get("/service-api/v1/search", params={"for": "ahriman"})

    assert response.ok
    assert await response.json() == [{"package": aur_package_ahriman.package_base,
                                      "description": aur_package_ahriman.description}]


async def test_get_exception(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise 400 on empty search string
    """
    search_mock = mocker.patch("ahriman.core.alpm.remote.AUR.multisearch", return_value=[])
    response = await client.get("/service-api/v1/search")

    assert response.status == 404
    search_mock.assert_called_once_with(pacman=pytest.helpers.anyvar(int))


async def test_get_join(client: TestClient, mocker: MockerFixture) -> None:
    """
    must join search args with space
    """
    search_mock = mocker.patch("ahriman.core.alpm.remote.AUR.multisearch")
    response = await client.get("/service-api/v1/search", params=[("for", "ahriman"), ("for", "maybe")])

    assert response.ok
    search_mock.assert_called_once_with("ahriman", "maybe", pacman=pytest.helpers.anyvar(int))
