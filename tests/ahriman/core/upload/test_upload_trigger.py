from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.upload import UploadTrigger
from ahriman.models.result import Result


def test_run(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run report for specified targets
    """
    configuration.set_option("upload", "target", "rsync")
    run_mock = mocker.patch("ahriman.core.upload.Upload.run")

    trigger = UploadTrigger("x86_64", configuration)
    trigger.run(Result(), [])
    run_mock.assert_called_once_with(configuration.repository_paths.repository, [])
