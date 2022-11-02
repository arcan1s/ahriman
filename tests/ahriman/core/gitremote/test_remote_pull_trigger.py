from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.gitremote import RemotePullTrigger


def test_on_start(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must clone repo on start
    """
    run_mock = mocker.patch("ahriman.core.gitremote.remote_pull.RemotePull.run")
    trigger = RemotePullTrigger("x86_64", configuration)

    trigger.on_start()
    run_mock.assert_called_once_with()
