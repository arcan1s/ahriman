import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.handlers import Web
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.parser = lambda: True
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    setup_mock = mocker.patch("ahriman.web.web.setup_service")
    run_mock = mocker.patch("ahriman.web.web.run_server")
    start_mock = mocker.patch("ahriman.core.spawn.Spawn.start")
    stop_mock = mocker.patch("ahriman.core.spawn.Spawn.stop")
    join_mock = mocker.patch("ahriman.core.spawn.Spawn.join")

    Web.run(args, "x86_64", configuration, report=False, unsafe=False)
    setup_mock.assert_called_once_with("x86_64", configuration, pytest.helpers.anyvar(int))
    run_mock.assert_called_once_with(pytest.helpers.anyvar(int))
    start_mock.assert_called_once_with()
    stop_mock.assert_called_once_with()
    join_mock.assert_called_once_with()


def test_disallow_auto_architecture_run() -> None:
    """
    must not allow auto architecture run
    """
    assert not Web.ALLOW_AUTO_ARCHITECTURE_RUN


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Web.ALLOW_MULTI_ARCHITECTURE_RUN
