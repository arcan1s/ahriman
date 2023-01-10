from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.gitremote import RemotePushTrigger
from ahriman.models.context_key import ContextKey
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
                   database: SQLite, mocker: MockerFixture) -> None:
    """
    must push changes on result
    """
    database_mock = mocker.patch("ahriman.core._Context.get", return_value=database)
    run_mock = mocker.patch("ahriman.core.gitremote.remote_push.RemotePush.run")
    trigger = RemotePushTrigger("x86_64", configuration)

    trigger.on_result(result, [package_ahriman])
    database_mock.assert_called_once_with(ContextKey("database", SQLite))
    run_mock.assert_called_once_with(result)
