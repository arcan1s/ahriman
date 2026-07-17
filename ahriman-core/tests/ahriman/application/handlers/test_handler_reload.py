import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers.reload import Reload
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    run_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.configuration_reload")

    _, repository_id = configuration.check_loaded()
    Reload.run(args, repository_id, configuration, report=False)
    run_mock.assert_called_once_with()


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Reload.ALLOW_MULTI_ARCHITECTURE_RUN
