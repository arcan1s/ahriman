import argparse

from pytest_mock import MockerFixture

from ahriman.application.ahriman import _parser
from ahriman.application.handlers import Help
from ahriman.core.configuration import Configuration


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.parser = _parser
    args.command = None
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    parse_mock = mocker.patch("argparse.ArgumentParser.parse_args")

    Help.run(args, "x86_64", configuration, report=False, unsafe=False)
    parse_mock.assert_called_once_with(["--help"])


def test_run_command(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command for specific subcommand
    """
    args = _default_args(args)
    args.command = "aur-search"
    parse_mock = mocker.patch("argparse.ArgumentParser.parse_args")

    Help.run(args, "x86_64", configuration, report=False, unsafe=False)
    parse_mock.assert_called_once_with(["aur-search", "--help"])


def test_disallow_auto_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Help.ALLOW_AUTO_ARCHITECTURE_RUN
