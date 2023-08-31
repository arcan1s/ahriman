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

    _, repository_id = configuration.check_loaded()
    Shell.run(args, repository_id, configuration, report=False)
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

    _, repository_id = configuration.check_loaded()
    Shell.run(args, repository_id, configuration, report=False)
    application_mock.assert_called_once_with(args.code)


def test_run_verbose(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                     mocker: MockerFixture) -> None:
    """
    must run command with verbose option
    """
    args = _default_args(args)
    args.verbose = True
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    read_mock = mocker.patch("pathlib.Path.read_text", return_value="")
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")
    application_mock = mocker.patch("code.interact")

    _, repository_id = configuration.check_loaded()
    Shell.run(args, repository_id, configuration, report=False)
    application_mock.assert_called_once_with(local=pytest.helpers.anyvar(int))
    read_mock.assert_called_once_with(encoding="utf8")
    print_mock.assert_called_once_with(verbose=False)


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Shell.ALLOW_MULTI_ARCHITECTURE_RUN
