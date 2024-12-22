import pytest

from aiohttp import FormData
from aiohttp.test_utils import TestClient
from aiohttp.web import HTTPBadRequest
from io import BytesIO
from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import AsyncMock, MagicMock, call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.models.repository_paths import RepositoryPaths
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.service.upload import UploadView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("POST",):
        request = pytest.helpers.request("", "", method)
        assert await UploadView.get_permission(request) == UserAccess.Full


def test_routes() -> None:
    """
    must return correct routes
    """
    assert UploadView.ROUTES == ["/api/v1/service/upload"]


def test_routes_dynamic(configuration: Configuration) -> None:
    """
    must correctly return upload url
    """
    assert UploadView.ROUTES == UploadView.routes(configuration)


def test_routes_dynamic_not_found(configuration: Configuration) -> None:
    """
    must disable upload route if option is not set
    """
    configuration.set_option("web", "enable_archive_upload", "no")
    assert UploadView.routes(configuration) == []


async def test_save_file(mocker: MockerFixture) -> None:
    """
    must correctly save file
    """
    part_mock = MagicMock()
    part_mock.filename = "filename"
    part_mock.read_chunk = AsyncMock(side_effect=[b"content", None])

    tempfile_mock = mocker.patch("ahriman.web.views.v1.service.upload.NamedTemporaryFile")
    file_mock = MagicMock()
    tempfile_mock.return_value.__enter__.return_value = file_mock

    open_mock = mocker.patch("pathlib.Path.open")
    copy_mock = mocker.patch("shutil.copyfileobj")
    local = Path("local")

    assert await UploadView.save_file(part_mock, local, max_body_size=None) == \
        (part_mock.filename, local / f".{part_mock.filename}")
    file_mock.write.assert_called_once_with(b"content")
    open_mock.assert_called_once_with("wb")
    copy_mock.assert_called_once_with(pytest.helpers.anyvar(int), pytest.helpers.anyvar(int))


async def test_save_file_no_filename() -> None:
    """
    must raise exception on missing filename
    """
    part_mock = MagicMock()
    part_mock.filename = None

    with pytest.raises(HTTPBadRequest):
        await UploadView.save_file(part_mock, Path("local"), max_body_size=None)


async def test_save_file_invalid_filename() -> None:
    """
    must raise exception on invalid filename
    """
    part_mock = MagicMock()
    part_mock.filename = ".."

    with pytest.raises(HTTPBadRequest):
        await UploadView.save_file(part_mock, Path("local"), max_body_size=None)


async def test_save_file_too_big() -> None:
    """
    must raise exception on too big file
    """
    part_mock = MagicMock()
    part_mock.filename = "filename"
    part_mock.read_chunk = AsyncMock(side_effect=[b"content", None])

    with pytest.raises(HTTPBadRequest):
        await UploadView.save_file(part_mock, Path("local"), max_body_size=0)


async def test_post(client: TestClient, repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must process file upload via http
    """
    local = Path("local")
    save_mock = pytest.helpers.patch_view(client.app, "save_file",
                                          AsyncMock(return_value=("filename", local / ".filename")))
    rename_mock = mocker.patch("pathlib.Path.rename")
    # no content validation here because it has invalid schema

    data = FormData()
    data.add_field("package", BytesIO(b"content"), filename="filename", content_type="application/octet-stream")

    response = await client.post("/api/v1/service/upload", data=data)
    assert response.ok
    save_mock.assert_called_once_with(pytest.helpers.anyvar(int), repository_paths.packages, max_body_size=None)
    rename_mock.assert_called_once_with(local / "filename")


async def test_post_with_sig(client: TestClient, repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must process file upload with signature via http
    """
    local = Path("local")
    save_mock = pytest.helpers.patch_view(client.app, "save_file",
                                          AsyncMock(side_effect=[
                                              ("filename", local / ".filename"),
                                              ("filename.sig", local / ".filename.sig"),
                                          ]))
    rename_mock = mocker.patch("pathlib.Path.rename")
    # no content validation here because it has invalid schema

    data = FormData()
    data.add_field("package", BytesIO(b"content"), filename="filename")
    data.add_field("signature", BytesIO(b"sig"), filename="filename.sig")

    response = await client.post("/api/v1/service/upload", data=data)
    assert response.ok
    save_mock.assert_has_calls([
        MockCall(pytest.helpers.anyvar(int), repository_paths.packages, max_body_size=None),
        MockCall(pytest.helpers.anyvar(int), repository_paths.packages, max_body_size=None),
    ])
    rename_mock.assert_has_calls([
        MockCall(local / "filename"),
        MockCall(local / "filename.sig"),
    ])


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
    data.add_field("package", BytesIO(b"content"), filename="filename", content_type="application/octet-stream")

    response = await client.post("/api/v1/service/upload", data=data)
    assert response.status == 400
    assert not response_schema.validate(await response.json())


async def test_post_not_package(client: TestClient) -> None:
    """
    must return 400 on invalid multipart key
    """
    response_schema = pytest.helpers.schema_response(UploadView.post, code=400)
    data = FormData()
    data.add_field("random", BytesIO(b"content"), filename="filename", content_type="application/octet-stream")

    response = await client.post("/api/v1/service/upload", data=data)
    assert response.status == 400
    assert not response_schema.validate(await response.json())
