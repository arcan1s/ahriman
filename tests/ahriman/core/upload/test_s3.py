from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any, List, Optional, Tuple
from unittest import mock
from unittest.mock import MagicMock

from ahriman.core.upload import S3


_chunk_size = 8 * 1024 * 1024


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
    assert S3.calculate_etag(path, _chunk_size) == "c0aaf6ebf95ca9206dc8ba1d8ff10af3"


def test_files_remove(s3_remote_objects: List[Any]) -> None:
    """
    must remove remote objects
    """
    local_files = {
        Path(item.key): item.e_tag for item in s3_remote_objects if item.key != "x86_64/a"
    }
    remote_objects = {Path(item.key): item for item in s3_remote_objects}

    S3.files_remove(local_files, remote_objects)
    remote_objects[Path("x86_64/a")].delete.assert_called_once_with()


def test_files_upload(s3: S3, s3_remote_objects: List[Any], mocker: MockerFixture) -> None:
    """
    must upload changed files
    """
    def mimetype(path: Path) -> Tuple[Optional[str], None]:
        return ("text/html", None) if path.name == "b" else (None, None)

    root = Path("path")
    local_files = {
        Path(item.key.replace("a", "d")): item.e_tag.replace("b", "d").replace("\"", "")
        for item in s3_remote_objects
    }
    remote_objects = {Path(item.key): item for item in s3_remote_objects}

    mocker.patch("mimetypes.guess_type", side_effect=mimetype)
    upload_mock = s3.bucket = MagicMock()

    s3.files_upload(root, local_files, remote_objects)
    upload_mock.upload_file.assert_has_calls(
        [
            mock.call(
                Filename=str(root / s3.architecture / "b"),
                Key=f"{s3.architecture}/{s3.architecture}/b",
                ExtraArgs={"ContentType": "text/html"}),
            mock.call(
                Filename=str(root / s3.architecture / "d"),
                Key=f"{s3.architecture}/{s3.architecture}/d",
                ExtraArgs=None),
        ],
        any_order=True)


def test_get_local_files(s3: S3, resource_path_root: Path, mocker: MockerFixture) -> None:
    """
    must get all local files recursively
    """
    walk_mock = mocker.patch("ahriman.core.util.walk")
    s3.get_local_files(resource_path_root)
    walk_mock.assert_called()


def test_get_remote_objects(s3: S3, s3_remote_objects: List[Any]) -> None:
    """
    must generate list of remote objects by calling boto3 function
    """
    expected = {Path(item.key).relative_to(s3.architecture): item for item in s3_remote_objects}

    s3.bucket = MagicMock()
    s3.bucket.objects.filter.return_value = s3_remote_objects

    assert s3.get_remote_objects() == expected


def test_sync(s3: S3, mocker: MockerFixture) -> None:
    """
    must run sync command
    """
    local_files_mock = mocker.patch("ahriman.core.upload.S3.get_local_files", return_value=["a"])
    remote_objects_mock = mocker.patch("ahriman.core.upload.S3.get_remote_objects", return_value=["b"])
    remove_files_mock = mocker.patch("ahriman.core.upload.S3.files_remove")
    upload_files_mock = mocker.patch("ahriman.core.upload.S3.files_upload")

    s3.sync(Path("root"), [])
    remote_objects_mock.assert_called_once_with()
    local_files_mock.assert_called_once_with(Path("root"))
    upload_files_mock.assert_called_once_with(Path("root"), ["a"], ["b"])
    remove_files_mock.assert_called_once_with(["a"], ["b"])
