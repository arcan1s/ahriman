import pytest

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import SynchronizationError
from ahriman.core.upload.upload import Upload
from ahriman.models.upload_settings import UploadSettings


def test_upload_failure(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must raise SyncFailed on errors
    """
    mocker.patch("ahriman.core.upload.rsync.Rsync.sync", side_effect=Exception())
    with pytest.raises(SynchronizationError):
        Upload.load("x86_64", configuration, "rsync").run(Path("path"), [])


def test_report_dummy(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must construct dummy upload class
    """
    mocker.patch("ahriman.models.upload_settings.UploadSettings.from_option", return_value=UploadSettings.Disabled)
    upload_mock = mocker.patch("ahriman.core.upload.upload.Upload.sync")
    Upload.load("x86_64", configuration, "disabled").run(Path("path"), [])
    upload_mock.assert_called_once_with(Path("path"), [])


def test_upload_rsync(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must upload via rsync
    """
    upload_mock = mocker.patch("ahriman.core.upload.rsync.Rsync.sync")
    Upload.load("x86_64", configuration, "rsync").run(Path("path"), [])
    upload_mock.assert_called_once_with(Path("path"), [])


def test_upload_s3(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must upload via s3
    """
    upload_mock = mocker.patch("ahriman.core.upload.s3.S3.sync")
    Upload.load("x86_64", configuration, "customs3").run(Path("path"), [])
    upload_mock.assert_called_once_with(Path("path"), [])


def test_upload_github(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must upload via github
    """
    upload_mock = mocker.patch("ahriman.core.upload.github.Github.sync")
    Upload.load("x86_64", configuration, "github").run(Path("path"), [])
    upload_mock.assert_called_once_with(Path("path"), [])
