import pytest
import requests

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.upload.github import Github
from ahriman.core.upload.http_upload import HttpUpload


def test_calculate_hash_empty(resource_path_root: Path) -> None:
    """
    must calculate checksum for empty file correctly
    """
    path = resource_path_root / "models" / "empty_file_checksum"
    assert HttpUpload.calculate_hash(path) == "d41d8cd98f00b204e9800998ecf8427e"


def test_calculate_hash_small(resource_path_root: Path) -> None:
    """
    must calculate checksum for path which is single chunk
    """
    path = resource_path_root / "models" / "package_ahriman_srcinfo"
    assert HttpUpload.calculate_hash(path) == "79b0f84e0232ed34fd191a85c383ecc5"


def test_get_body_get_hashes() -> None:
    """
    must generate readable body
    """
    source = {Path("c"): "c_md5", Path("a"): "a_md5", Path("b"): "b_md5"}
    body = HttpUpload.get_body(source)
    parsed = HttpUpload.get_hashes(body)
    assert {fn.name: md5 for fn, md5 in source.items()} == parsed


def test_get_hashes_empty() -> None:
    """
    must read empty body
    """
    assert HttpUpload.get_hashes("") == {}


def test_request(github: Github, mocker: MockerFixture) -> None:
    """
    must call request method
    """
    response_mock = MagicMock()
    request_mock = mocker.patch("requests.request", return_value=response_mock)

    github._request("GET", "url", arg="arg")
    request_mock.assert_called_once_with("GET", "url", auth=github.auth, timeout=github.timeout, arg="arg")
    response_mock.raise_for_status.assert_called_once_with()


def test_request_exception(github: Github, mocker: MockerFixture) -> None:
    """
    must call request method and log HTTPError exception
    """
    mocker.patch("requests.request", side_effect=requests.HTTPError())
    with pytest.raises(requests.HTTPError):
        github._request("GET", "url", arg="arg")
