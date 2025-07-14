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
    mocker.patch("ahriman.core.upload.rsync.Rsync.sync", side_effect=Exception)
    _, repository_id = configuration.check_loaded()

    with pytest.raises(SynchronizationError):
        Upload.load(repository_id, configuration, "rsync").run(Path("path"), [])


def test_report_dummy(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must construct dummy upload class
    """
    mocker.patch("ahriman.models.upload_settings.UploadSettings.from_option", return_value=UploadSettings.Disabled)
    upload_mock = mocker.patch("ahriman.core.upload.upload.Upload.sync")
    _, repository_id = configuration.check_loaded()

    Upload.load(repository_id, configuration, "disabled").run(Path("path"), [])
    upload_mock.assert_called_once_with(Path("path"), [])


def test_upload_rsync(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must upload via rsync
    """
    upload_mock = mocker.patch("ahriman.core.upload.rsync.Rsync.sync")
    _, repository_id = configuration.check_loaded()

    Upload.load(repository_id, configuration, "rsync").run(Path("path"), [])
    upload_mock.assert_called_once_with(Path("path"), [])


def test_upload_s3(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must upload via s3
    """
    upload_mock = mocker.patch("ahriman.core.upload.s3.S3.sync")
    _, repository_id = configuration.check_loaded()

    Upload.load(repository_id, configuration, "customs3").run(Path("path"), [])
    upload_mock.assert_called_once_with(Path("path"), [])


def test_upload_github(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must upload via github
    """
    upload_mock = mocker.patch("ahriman.core.upload.github.GitHub.sync")
    _, repository_id = configuration.check_loaded()

    Upload.load(repository_id, configuration, "github").run(Path("path"), [])
    upload_mock.assert_called_once_with(Path("path"), [])


def test_upload_ahriman(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must upload via ahriman
    """
    upload_mock = mocker.patch("ahriman.core.upload.remote_service.RemoteService.sync")
    configuration.set_option("web", "host", "localhost")
    configuration.set_option("web", "port", "8080")
    _, repository_id = configuration.check_loaded()

    Upload.load(repository_id, configuration, "remote-service").run(Path("path"), [])
    upload_mock.assert_called_once_with(Path("path"), [])
