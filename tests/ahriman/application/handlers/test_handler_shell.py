import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.handlers import Shell
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
    args.code = None
    args.verbose = False
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    application_mock = mocker.patch("code.interact")

    Shell.run(args, "x86_64", configuration, report=False, unsafe=False)
    application_mock.assert_called_once_with(local=pytest.helpers.anyvar(int))


def test_run_eval(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                  mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    args.code = """print("hello world")"""
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    application_mock = mocker.patch("code.InteractiveConsole.runcode")

    Shell.run(args, "x86_64", configuration, report=False, unsafe=False)
    application_mock.assert_called_once_with(args.code)


def test_run_verbose(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                     mocker: MockerFixture) -> None:
    """
    must run command with verbose option
    """
    args = _default_args(args)
    args.verbose = True
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")
    application_mock = mocker.patch("code.interact")

    Shell.run(args, "x86_64", configuration, report=False, unsafe=False)
    application_mock.assert_called_once_with(local=pytest.helpers.anyvar(int))
    print_mock.assert_called_once_with(verbose=False)
