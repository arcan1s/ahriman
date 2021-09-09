from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture


async def test_post(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call post request correctly
    """
    add_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_remove")
    response = await client.post("/service-api/v1/remove", json={"packages": ["ahriman"]})

    assert response.status == 200
    add_mock.assert_called_with(["ahriman"])


async def test_post_exception(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise exception on missing packages payload
    """
    add_mock = mocker.patch("ahriman.core.spawn.Spawn.packages_remove")
    response = await client.post("/service-api/v1/remove")

    assert response.status == 400
    add_mock.assert_not_called()
