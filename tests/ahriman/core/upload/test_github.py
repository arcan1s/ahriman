import pytest
import requests

from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any
from unittest.mock import call as MockCall

from ahriman.core.upload.github import Github


def test_asset_remove(github: Github, github_release: dict[str, Any], mocker: MockerFixture) -> None:
    """
    must remove asset from the release
    """
    request_mock = mocker.patch("ahriman.core.upload.github.Github.make_request")
    github.asset_remove(github_release, "asset_name")
    request_mock.assert_called_once_with("DELETE", "asset_url")


def test_asset_remove_unknown(github: Github, github_release: dict[str, Any], mocker: MockerFixture) -> None:
    """
    must not fail if no asset found
    """
    request_mock = mocker.patch("ahriman.core.upload.github.Github.make_request")
    github.asset_remove(github_release, "unknown_asset_name")
    request_mock.assert_not_called()


def test_asset_upload(github: Github, github_release: dict[str, Any], mocker: MockerFixture) -> None:
    """
    must upload asset to the repository
    """
    mocker.patch("pathlib.Path.open")
    request_mock = mocker.patch("ahriman.core.upload.github.Github.make_request")
    remove_mock = mocker.patch("ahriman.core.upload.github.Github.asset_remove")

    github.asset_upload(github_release, Path("/root/new.tar.xz"))
    request_mock.assert_called_once_with("POST", "upload_url", params=[("name", "new.tar.xz")],
                                         data=pytest.helpers.anyvar(int),
                                         headers={"Content-Type": "application/x-tar"})
    remove_mock.assert_not_called()


def test_asset_upload_with_removal(github: Github, github_release: dict[str, Any], mocker: MockerFixture) -> None:
    """
    must remove existing file before upload
    """
    mocker.patch("pathlib.Path.open")
    mocker.patch("ahriman.core.upload.github.Github.make_request")
    remove_mock = mocker.patch("ahriman.core.upload.github.Github.asset_remove")

    github.asset_upload(github_release, Path("asset_name"))
    github.asset_upload(github_release, Path("/root/asset_name"))
    remove_mock.assert_has_calls([
        MockCall(github_release, "asset_name"),
        MockCall(github_release, "asset_name"),
    ])


def test_asset_upload_empty_mimetype(github: Github, github_release: dict[str, Any], mocker: MockerFixture) -> None:
    """
    must upload asset to the repository with empty mime type if the library cannot guess it
    """
    mocker.patch("pathlib.Path.open")
    mocker.patch("ahriman.core.upload.github.Github.asset_remove")
    mocker.patch("mimetypes.guess_type", return_value=(None, None))
    request_mock = mocker.patch("ahriman.core.upload.github.Github.make_request")

    github.asset_upload(github_release, Path("/root/new.tar.xz"))
    request_mock.assert_called_once_with("POST", "upload_url", params=[("name", "new.tar.xz")],
                                         data=pytest.helpers.anyvar(int),
                                         headers={"Content-Type": "application/octet-stream"})


def test_get_local_files(github: Github, resource_path_root: Path, mocker: MockerFixture) -> None:
    """
    must get all local files recursively
    """
    walk_mock = mocker.patch("ahriman.core.util.walk")
    github.get_local_files(resource_path_root)
    walk_mock.assert_called()


def test_files_remove(github: Github, github_release: dict[str, Any], mocker: MockerFixture) -> None:
    """
    must remove files from the remote
    """
    remove_mock = mocker.patch("ahriman.core.upload.github.Github.asset_remove")
    github.files_remove(github_release, {Path("a"): "a"}, {"a": "a", "b": "b"})
    remove_mock.assert_called_once_with(github_release, "b")


def test_files_remove_empty(github: Github, github_release: dict[str, Any], mocker: MockerFixture) -> None:
    """
    must remove nothing if nothing changed
    """
    remove_mock = mocker.patch("ahriman.core.upload.github.Github.asset_remove")
    github.files_remove(github_release, {Path("a"): "a"}, {"a": "a"})
    remove_mock.assert_not_called()


def test_files_upload(github: Github, github_release: dict[str, Any], mocker: MockerFixture) -> None:
    """
    must upload files to the remote
    """
    upload_mock = mocker.patch("ahriman.core.upload.github.Github.asset_upload")
    github.files_upload(github_release, {Path("a"): "a", Path("b"): "c", Path("c"): "c"}, {"a": "a", "b": "b"})
    upload_mock.assert_has_calls([
        MockCall(github_release, Path("b")),
        MockCall(github_release, Path("c")),
    ])


def test_files_upload_empty(github: Github, github_release: dict[str, Any], mocker: MockerFixture) -> None:
    """
    must upload nothing if nothing changed
    """
    upload_mock = mocker.patch("ahriman.core.upload.github.Github.asset_upload")
    github.files_upload(github_release, {Path("a"): "a"}, {"a": "a"})
    upload_mock.assert_not_called()


def test_release_create(github: Github, mocker: MockerFixture) -> None:
    """
    must create release
    """
    request_mock = mocker.patch("ahriman.core.upload.github.Github.make_request")
    github.release_create()
    request_mock.assert_called_once_with("POST", pytest.helpers.anyvar(str, True),
                                         json={"tag_name": github.architecture, "name": github.architecture})


def test_release_get(github: Github, mocker: MockerFixture) -> None:
    """
    must get release
    """
    request_mock = mocker.patch("ahriman.core.upload.github.Github.make_request")
    github.release_get()
    request_mock.assert_called_once_with("GET", pytest.helpers.anyvar(str, True))


def test_release_get_empty(github: Github, mocker: MockerFixture) -> None:
    """
    must return nothing in case of 404 status code
    """
    response = requests.Response()
    response.status_code = 404
    mocker.patch("ahriman.core.upload.github.Github.make_request",
                 side_effect=requests.HTTPError(response=response))
    assert github.release_get() is None


def test_release_get_exception(github: Github, mocker: MockerFixture) -> None:
    """
    must re-raise non HTTPError exception
    """
    mocker.patch("ahriman.core.upload.github.Github.make_request", side_effect=Exception())
    with pytest.raises(Exception):
        github.release_get()


def test_release_get_exception_http_error(github: Github, mocker: MockerFixture) -> None:
    """
    must re-raise HTTPError exception with code differs from 404
    """
    exception = requests.HTTPError(response=requests.Response())
    mocker.patch("ahriman.core.upload.github.Github.make_request", side_effect=exception)
    with pytest.raises(requests.HTTPError):
        github.release_get()


def test_release_update(github: Github, github_release: dict[str, Any], mocker: MockerFixture) -> None:
    """
    must update release
    """
    request_mock = mocker.patch("ahriman.core.upload.github.Github.make_request")
    github.release_update(github_release, "body")
    request_mock.assert_called_once_with("POST", "release_url", json={"body": "body"})


def test_release_sync(github: Github, mocker: MockerFixture) -> None:
    """
    must run sync command
    """
    release_get_mock = mocker.patch("ahriman.core.upload.github.Github.release_get", return_value={})
    get_hashes_mock = mocker.patch("ahriman.core.upload.github.Github.get_hashes", return_value={})
    get_local_files_mock = mocker.patch("ahriman.core.upload.github.Github.get_local_files", return_value={})
    files_upload_mock = mocker.patch("ahriman.core.upload.github.Github.files_upload")
    files_remove_mock = mocker.patch("ahriman.core.upload.github.Github.files_remove")
    release_update_mock = mocker.patch("ahriman.core.upload.github.Github.release_update")

    github.sync(Path("local"), [])
    release_get_mock.assert_called_once_with()
    get_hashes_mock.assert_called_once_with("")
    get_local_files_mock.assert_called_once_with(Path("local"))
    files_upload_mock.assert_called_once_with({}, {}, {})
    files_remove_mock.assert_called_once_with({}, {}, {})
    release_update_mock.assert_called_once_with({}, pytest.helpers.anyvar(int))


def test_release_sync_create_release(github: Github, mocker: MockerFixture) -> None:
    """
    must create release in case if it does not exist
    """
    mocker.patch("ahriman.core.upload.github.Github.release_get", return_value=None)
    mocker.patch("ahriman.core.upload.github.Github.get_hashes")
    mocker.patch("ahriman.core.upload.github.Github.get_local_files")
    mocker.patch("ahriman.core.upload.github.Github.files_upload")
    mocker.patch("ahriman.core.upload.github.Github.files_remove")
    mocker.patch("ahriman.core.upload.github.Github.release_update")
    release_create_mock = mocker.patch("ahriman.core.upload.github.Github.release_create")

    github.sync(Path("local"), [])
    release_create_mock.assert_called_once_with()
