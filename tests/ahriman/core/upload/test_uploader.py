import pytest

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import SyncFailed
from ahriman.core.upload.upload import Upload
from ahriman.models.upload_settings import UploadSettings


def test_upload_failure(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must raise SyncFailed on errors
    """
    mocker.patch("ahriman.core.upload.rsync.Rsync.sync", side_effect=Exception())
    with pytest.raises(SyncFailed):
        Upload.run("x86_64", configuration, UploadSettings.Rsync.name, Path("path"))


def test_upload_rsync(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must upload via rsync
    """
    upload_mock = mocker.patch("ahriman.core.upload.rsync.Rsync.sync")
    Upload.run("x86_64", configuration, UploadSettings.Rsync.name, Path("path"))
    upload_mock.assert_called_once()


def test_upload_s3(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must upload via s3
    """
    upload_mock = mocker.patch("ahriman.core.upload.s3.S3.sync")
    Upload.run("x86_64", configuration, UploadSettings.S3.name, Path("path"))
    upload_mock.assert_called_once()
