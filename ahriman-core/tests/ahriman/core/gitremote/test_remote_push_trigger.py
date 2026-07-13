from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.gitremote import RemotePushTrigger
from ahriman.core.status import Client
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_configuration_sections(configuration: Configuration) -> None:
    """
    must correctly parse target list
    """
    configuration.set_option("remote-push", "target", "a b c")
    assert RemotePushTrigger.configuration_sections(configuration) == ["a", "b", "c"]

    configuration.remove_option("remote-push", "target")
    assert RemotePushTrigger.configuration_sections(configuration) == []


def test_on_result(configuration: Configuration, result: Result, package_ahriman: Package,
                   local_client: Client, mocker: MockerFixture) -> None:
    """
    must push changes on result
    """
    database_mock = mocker.patch("ahriman.core._Context.get", return_value=local_client)
    run_mock = mocker.patch("ahriman.core.gitremote.remote_push.RemotePush.run")
    _, repository_id = configuration.check_loaded()
    trigger = RemotePushTrigger(repository_id, configuration)

    trigger.on_result(result, [package_ahriman])
    database_mock.assert_called_once_with(Client)
    run_mock.assert_called_once_with(result)
