from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any
from unittest.mock import MagicMock, call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.core.upload.s3 import S3
from ahriman.models.repository_paths import RepositoryPaths


_chunk_size = 8 * 1024 * 1024


def test_object_path(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must correctly read object path
    """
    _, repository_id = configuration.check_loaded()

    # new-style tree
    assert S3(repository_id, configuration, "customs3").object_path == Path("aur-clone/x86_64")

    # legacy tree
    mocker.patch.object(RepositoryPaths, "_suffix", Path("x86_64"))
    assert S3(repository_id, configuration, "customs3").object_path == Path("x86_64")

    # user defined prefix
    configuration.set_option("customs3", "object_path", "local")
    assert S3(repository_id, configuration, "customs3").object_path == Path("local")


def test_calculate_etag_big(resource_path_root: Path) -> None:
    """
    must calculate checksum for path which is more than one chunk
    """
    path = resource_path_root / "models" / "big_file_checksum"
    assert S3.calculate_etag(path, _chunk_size) == "3b15154eaeed22ae19ae4667d4b98d28-2"


def test_calculate_etag_empty(resource_path_root: Path) -> None:
    """
    must calculate checksum for empty file correctly
    """
    path = resource_path_root / "models" / "empty_file_checksum"
    assert S3.calculate_etag(path, _chunk_size) == "d41d8cd98f00b204e9800998ecf8427e"


def test_calculate_etag_small(resource_path_root: Path) -> None:
    """
    must calculate checksum for path which is single chunk
    """
    path = resource_path_root / "models" / "package_ahriman_srcinfo"
    assert S3.calculate_etag(path, _chunk_size) == "2635e2898452d594025517cfe529b1f2"


def test_files_remove(s3_remote_objects: list[Any]) -> None:
    """
    must remove remote objects
    """
    local_files = {
        Path(item.key): item.e_tag for item in s3_remote_objects if item.key != "aur-clone/x86_64/a"
    }
    remote_objects = {Path(item.key): item for item in s3_remote_objects}

    S3.files_remove(local_files, remote_objects)
    remote_objects[Path("aur-clone/x86_64/a")].delete.assert_called_once_with()


def test_files_upload(s3: S3, s3_remote_objects: list[Any], mocker: MockerFixture) -> None:
    """
    must upload changed files
    """
    def mimetype(path: Path) -> tuple[str | None, None]:
        return ("text/html", None) if path.name == "b" else (None, None)

    root = Path("path")
    local_files = {
        Path(item.key[:-1] + item.key[-1].replace("a", "d")): item.e_tag.replace("b", "d").replace("\"", "")
        for item in s3_remote_objects
    }
    print(local_files)
    remote_objects = {Path(item.key): item for item in s3_remote_objects}

    mocker.patch("mimetypes.guess_type", side_effect=mimetype)
    upload_mock = s3.bucket = MagicMock()

    s3.files_upload(root, local_files, remote_objects)
    upload_mock.upload_file.assert_has_calls(
        [
            MockCall(
                Filename=str(root / s3.object_path / "b"),
                Key=f"{s3.object_path}/b",
                ExtraArgs={"ContentType": "text/html"}),
            MockCall(
                Filename=str(root / s3.object_path / "d"),
                Key=f"{s3.object_path}/d",
                ExtraArgs=None),
        ],
        any_order=True)


def test_get_local_files(s3: S3, resource_path_root: Path, mocker: MockerFixture) -> None:
    """
    must get all local files recursively
    """
    walk_mock = mocker.patch("ahriman.core.utils.walk")
    s3.get_local_files(resource_path_root)
    walk_mock.assert_called()


def test_get_remote_objects(s3: S3, s3_remote_objects: list[Any]) -> None:
    """
    must generate list of remote objects by calling boto3 function
    """
    expected = {Path(item.key).relative_to(s3.object_path): item for item in s3_remote_objects}

    s3.bucket = MagicMock()
    s3.bucket.objects.filter.return_value = s3_remote_objects

    assert s3.get_remote_objects() == expected


def test_sync(s3: S3, mocker: MockerFixture) -> None:
    """
    must run sync command
    """
    local_files_mock = mocker.patch("ahriman.core.upload.s3.S3.get_local_files", return_value=["a"])
    remote_objects_mock = mocker.patch("ahriman.core.upload.s3.S3.get_remote_objects", return_value=["b"])
    remove_files_mock = mocker.patch("ahriman.core.upload.s3.S3.files_remove")
    upload_files_mock = mocker.patch("ahriman.core.upload.s3.S3.files_upload")

    s3.sync(Path("root"), [])
    remote_objects_mock.assert_called_once_with()
    local_files_mock.assert_called_once_with(Path("root"))
    upload_files_mock.assert_called_once_with(Path("root"), ["a"], ["b"])
    remove_files_mock.assert_called_once_with(["a"], ["b"])
