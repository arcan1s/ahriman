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
    args.aur = True
    args.local = True
    args.manual = True
    args.vcs = True
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    run_mock = mocker.patch("ahriman.application.handlers.Update.run")
    start_mock = mocker.patch("threading.Timer.start")
    join_mock = mocker.patch("threading.Timer.join")

    Daemon.run(args, "x86_64", configuration, report=True, unsafe=False)
    run_mock.assert_called_once_with(args, "x86_64", configuration, report=True, unsafe=False)
    start_mock.assert_called_once_with()
    join_mock.assert_called_once_with()
