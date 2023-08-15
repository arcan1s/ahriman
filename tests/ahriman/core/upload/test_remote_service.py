import pytest

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.upload.remote_service import RemoteService
from ahriman.models.package import Package


def test_session(remote_service: RemoteService, mocker: MockerFixture) -> None:
    """
    must generate ahriman session
    """
    upload_mock = mocker.patch("ahriman.core.status.web_client.WebClient._create_session")
    assert remote_service.session
    upload_mock.assert_called_once_with(use_unix_socket=False)


def test_package_upload(remote_service: RemoteService, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must upload package to remote host
    """
    open_mock = mocker.patch("pathlib.Path.open")
    upload_mock = mocker.patch("ahriman.core.upload.http_upload.HttpUpload._request")
    filename = package_ahriman.packages[package_ahriman.base].filename

    remote_service.sync(Path("local"), [package_ahriman])
    open_mock.assert_called_once_with("rb")
    upload_mock.assert_called_once_with("POST", f"{remote_service.client.address}/api/v1/service/upload", files={
        "archive": (filename, pytest.helpers.anyvar(int), "application/octet-stream", {})
    })


def test_package_upload_no_filename(
        remote_service: RemoteService,
        package_ahriman: Package,
        mocker: MockerFixture) -> None:
    """
    must skip upload if no filename set
    """
    open_mock = mocker.patch("pathlib.Path.open")
    upload_mock = mocker.patch("ahriman.core.status.web_client.WebClient.make_request")
    package_ahriman.packages[package_ahriman.base].filename = None

    remote_service.sync(Path("local"), [package_ahriman])
    open_mock.assert_not_called()
    upload_mock.assert_not_called()


def test_sync(remote_service: RemoteService, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run sync command
    """
    upload_mock = mocker.patch("ahriman.core.upload.remote_service.RemoteService.package_upload")
    local = Path("local")

    remote_service.sync(local, [package_ahriman])
    upload_mock.assert_called_once_with(local, package_ahriman)
