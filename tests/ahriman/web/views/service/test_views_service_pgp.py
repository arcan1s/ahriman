import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture

from ahriman.models.user_access import UserAccess
from ahriman.web.views.service.pgp import PGPView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET", "HEAD"):
        request = pytest.helpers.request("", "", method)
        assert await PGPView.get_permission(request) == UserAccess.Reporter
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await PGPView.get_permission(request) == UserAccess.Full


async def test_get(client: TestClient, mocker: MockerFixture) -> None:
    """
    must retrieve key from the keyserver
    """
    import_mock = mocker.patch("ahriman.core.sign.gpg.GPG.key_download", return_value="imported")

    response = await client.get("/api/v1/service/pgp", params={"key": "0xdeadbeaf", "server": "keyserver.ubuntu.com"})
    assert response.ok
    import_mock.assert_called_once_with("keyserver.ubuntu.com", "0xdeadbeaf")
    assert await response.json() == {"key": "imported"}


async def test_get_empty(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise 400 on missing parameters
    """
    import_mock = mocker.patch("ahriman.core.sign.gpg.GPG.key_download")

    response = await client.get("/api/v1/service/pgp")
    assert response.status == 400
    import_mock.assert_not_called()


async def test_get_process_exception(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise 404 on invalid PGP server response
    """
    import_mock = mocker.patch("ahriman.core.sign.gpg.GPG.key_download", side_effect=Exception())

    response = await client.get("/api/v1/service/pgp", params={"key": "0xdeadbeaf", "server": "keyserver.ubuntu.com"})
    assert response.status == 404
    import_mock.assert_called_once_with("keyserver.ubuntu.com", "0xdeadbeaf")


async def test_post(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call post request correctly
    """
    import_mock = mocker.patch("ahriman.core.spawn.Spawn.key_import")

    response = await client.post("/api/v1/service/pgp", json={"key": "0xdeadbeaf", "server": "keyserver.ubuntu.com"})
    assert response.ok
    import_mock.assert_called_once_with("0xdeadbeaf", "keyserver.ubuntu.com")


async def test_post_exception(client: TestClient, mocker: MockerFixture) -> None:
    """
    must raise exception on missing key payload
    """
    import_mock = mocker.patch("ahriman.core.spawn.Spawn.key_import")

    response = await client.post("/api/v1/service/pgp")
    assert response.status == 400
    import_mock.assert_not_called()
