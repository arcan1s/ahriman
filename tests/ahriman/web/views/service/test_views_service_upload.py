import pytest

from aiohttp import FormData
from aiohttp.test_utils import TestClient
from io import BytesIO
from pytest_mock import MockerFixture

from ahriman.models.user_access import UserAccess
from ahriman.web.views.service.upload import UploadView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await UploadView.get_permission(request) == UserAccess.Full


async def test_post(client: TestClient, mocker: MockerFixture) -> None:
    """
    must call post request correctly for alias
    """
    open_mock = mocker.patch("pathlib.Path.open")
    # no content validation here because it has invalid schema

    data = FormData()
    data.add_field("archive", BytesIO(b"content"), filename="filename", content_type="application/octet-stream")

    response = await client.post("/api/v1/service/upload", data=data)
    assert response.ok
    open_mock.assert_called_once_with("wb")


async def test_post_not_multipart(client: TestClient) -> None:
    """
    must return 400 on invalid payload
    """
    response = await client.post("/api/v1/service/upload")
    assert response.status == 400


async def test_post_not_bodypart(client: TestClient, mocker: MockerFixture) -> None:
    """
    must return 400 on invalid iterator in multipart
    """
    mocker.patch("aiohttp.MultipartReader.next", return_value=42)  # surprise, motherfucker
    data = FormData()
    data.add_field("archive", BytesIO(b"content"), filename="filename", content_type="application/octet-stream")

    response = await client.post("/api/v1/service/upload", data=data)
    assert response.status == 400


async def test_post_not_archive(client: TestClient) -> None:
    """
    must return 400 on invalid multipart key
    """
    data = FormData()
    data.add_field("random", BytesIO(b"content"), filename="filename", content_type="application/octet-stream")

    response = await client.post("/api/v1/service/upload", data=data)
    assert response.status == 400


async def test_post_no_filename(client: TestClient, mocker: MockerFixture) -> None:
    """
    must return 400 if filename is not set
    """
    mocker.patch("aiohttp.BodyPartReader.filename", return_value=None)
    data = FormData()
    data.add_field("random", BytesIO(b"content"), filename="filename", content_type="application/octet-stream")

    response = await client.post("/api/v1/service/upload", data=data)
    assert response.status == 400


async def test_post_filename_invalid(client: TestClient) -> None:
    """
    must return 400 if filename is invalid
    """
    data = FormData()
    data.add_field("archive", BytesIO(b"content"), filename="..", content_type="application/octet-stream")
    response = await client.post("/api/v1/service/upload", data=data)
    assert response.status == 400

    data = FormData()
    data.add_field("archive", BytesIO(b"content"), filename="", content_type="application/octet-stream")
    response = await client.post("/api/v1/service/upload", data=data)
    assert response.status == 400
