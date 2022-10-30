import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Daemon
from ahriman.core.configuration import Configuration


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.interval = 60 * 60 * 12
    args.no_aur = False
    args.no_local = False
    args.no_manual = False
    args.no_vcs = False
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    run_mock = mocker.patch("ahriman.application.handlers.Update.run")
    start_mock = mocker.patch("threading.Timer.start")
    join_mock = mocker.patch("threading.Timer.join")

    Daemon.run(args, "x86_64", configuration, True, False)
    Daemon._SHOULD_RUN = False
    run_mock.assert_called_once_with(args, "x86_64", configuration, True, False)
    start_mock.assert_called_once_with()
    join_mock.assert_called_once_with()
