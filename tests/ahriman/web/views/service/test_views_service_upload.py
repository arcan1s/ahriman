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
    must process file upload via http
    """
    open_mock = mocker.patch("pathlib.Path.open")
    copy_mock = mocker.patch("shutil.copyfileobj")
    # no content validation here because it has invalid schema

    data = FormData()
    data.add_field("archive", BytesIO(b"content"), filename="filename", content_type="application/octet-stream")

    response = await client.post("/api/v1/service/upload", data=data)
    assert response.ok
    open_mock.assert_called_once_with("wb")
    copy_mock.assert_called_once_with(pytest.helpers.anyvar(int), pytest.helpers.anyvar(int))


async def test_post_not_found(client: TestClient, mocker: MockerFixture) -> None:
    """
    must return 404 if request was disabled
    """
    mocker.patch("ahriman.core.configuration.Configuration.getboolean", return_value=False)
    data = FormData()
    data.add_field("archive", BytesIO(b"content"), filename="filename", content_type="application/octet-stream")
    response_schema = pytest.helpers.schema_response(UploadView.post, code=404)

    response = await client.post("/api/v1/service/upload", data=data)
    assert response.status == 404
    assert not response_schema.validate(await response.json())


async def test_post_not_multipart(client: TestClient) -> None:
    """
    must return 400 on invalid payload
    """
    response_schema = pytest.helpers.schema_response(UploadView.post, code=400)

    response = await client.post("/api/v1/service/upload")
    assert response.status == 400
    assert not response_schema.validate(await response.json())


async def test_post_not_body_part(client: TestClient, mocker: MockerFixture) -> None:
    """
    must return 400 on invalid iterator in multipart
    """
    response_schema = pytest.helpers.schema_response(UploadView.post, code=400)
    mocker.patch("aiohttp.MultipartReader.next", return_value=42)  # surprise, motherfucker
    data = FormData()
    data.add_field("archive", BytesIO(b"content"), filename="filename", content_type="application/octet-stream")

    response = await client.post("/api/v1/service/upload", data=data)
    assert response.status == 400
    assert not response_schema.validate(await response.json())


async def test_post_not_archive(client: TestClient) -> None:
    """
    must return 400 on invalid multipart key
    """
    response_schema = pytest.helpers.schema_response(UploadView.post, code=400)
    data = FormData()
    data.add_field("random", BytesIO(b"content"), filename="filename", content_type="application/octet-stream")

    response = await client.post("/api/v1/service/upload", data=data)
    assert response.status == 400
    assert not response_schema.validate(await response.json())


async def test_post_filename_invalid(client: TestClient) -> None:
    """
    must return 400 if filename is invalid
    """
    response_schema = pytest.helpers.schema_response(UploadView.post, code=400)

    data = FormData()
    data.add_field("archive", BytesIO(b"content"), filename="..", content_type="application/octet-stream")
    response = await client.post("/api/v1/service/upload", data=data)
    assert response.status == 400
    assert not response_schema.validate(await response.json())


async def test_post_file_too_big(client: TestClient, mocker: MockerFixture) -> None:
    """
    must return 400 if file is too big
    """
    mocker.patch("pathlib.Path.open")
    mocker.patch("ahriman.core.configuration.Configuration.getint", return_value=0)
    data = FormData()
    data.add_field("archive", BytesIO(b"content"), filename="filename", content_type="application/octet-stream")
    response_schema = pytest.helpers.schema_response(UploadView.post, code=400)

    response = await client.post("/api/v1/service/upload", data=data)
    assert response.status == 400
    assert not response_schema.validate(await response.json())
