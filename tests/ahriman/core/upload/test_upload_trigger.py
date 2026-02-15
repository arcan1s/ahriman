from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.upload import UploadTrigger
from ahriman.models.result import Result


def test_configuration_sections(configuration: Configuration) -> None:
    """
    must correctly parse target list
    """
    configuration.set_option("upload", "target", "a b c")
    assert UploadTrigger.configuration_sections(configuration) == ["a", "b", "c"]

    configuration.remove_option("upload", "target")
    assert UploadTrigger.configuration_sections(configuration) == []


def test_on_result(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run report for specified targets
    """
    configuration.set_option("upload", "target", "rsync")
    run_mock = mocker.patch("ahriman.core.upload.upload.Upload.run")
    _, repository_id = configuration.check_loaded()

    trigger = UploadTrigger(repository_id, configuration)
    trigger.on_result(Result(), [])
    run_mock.assert_called_once_with(configuration.repository_paths.repository, [])
