from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture


async def test_post(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call post request correctly
    """
    add_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_add")
    response = await client.post("/service-api/v1/add", json={"packages": ["ahriman"]})

    assert response.status == 200
    add_mock.assert_called_with(["ahriman"], False)


async def test_post_now(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call post and run build
    """
    add_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_add")
    response = await client.post("/service-api/v1/add", json={"packages": ["ahriman"], "build_now": True})

    assert response.status == 200
    add_mock.assert_called_with(["ahriman"], True)


async def test_post_exception(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise exception on missing packages payload
    """
    add_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_add")
    response = await client.post("/service-api/v1/add")

    assert response.status == 400
    add_mock.assert_not_called()
