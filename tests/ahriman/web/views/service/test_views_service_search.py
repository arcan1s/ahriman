import aur

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture


async def test_get(client: TestClient, aur_package_ahriman: aur.Package, mocker: MockerFixture) -> None:
    """
    must call get request correctly
    """
    mocker.patch("aur.search", return_value=[aur_package_ahriman])
    response = await client.get("/service-api/v1/search", params={"for": "ahriman"})

    assert response.ok
    assert await response.json() == ["ahriman"]


async def test_get_exception(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise 400 on empty search string
    """
    search_mock = mocker.patch("aur.search")
    response = await client.get("/service-api/v1/search")

    assert response.status == 400
    search_mock.assert_not_called()


async def test_get_join(client: TestClient, mocker: MockerFixture) -> None:
    """
    must join search args with space
    """
    search_mock = mocker.patch("aur.search")
    response = await client.get("/service-api/v1/search", params=[("for", "ahriman"), ("for", "maybe")])

    assert response.ok
    search_mock.assert_called_with("ahriman maybe")


async def test_get_join_filter(client: TestClient, mocker: MockerFixture) -> None:
    """
    must filter search parameters with less than 3 symbols
    """
    search_mock = mocker.patch("aur.search")
    response = await client.get("/service-api/v1/search", params=[("for", "ah"), ("for", "maybe")])

    assert response.ok
    search_mock.assert_called_with("maybe")


async def test_get_join_filter_empty(client: TestClient, mocker: MockerFixture) -> None:
    """
    must filter search parameters with less than 3 symbols (empty result)
    """
    search_mock = mocker.patch("aur.search")
    response = await client.get("/service-api/v1/search", params=[("for", "ah"), ("for", "ma")])

    assert response.status == 400
    search_mock.assert_not_called()
