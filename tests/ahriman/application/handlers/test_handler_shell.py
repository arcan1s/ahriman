import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.handlers import Shell
from ahriman.core.configuration import Configuration


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.verbose = False
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("code.interact")

    Shell.run(args, "x86_64", configuration, report=False, unsafe=False)
    application_mock.assert_called_once_with(local=pytest.helpers.anyvar(int))


def test_run_verbose(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command with verbose option
    """
    args = _default_args(args)
    args.verbose = True
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")
    application_mock = mocker.patch("code.interact")

    Shell.run(args, "x86_64", configuration, report=False, unsafe=False)
    application_mock.assert_called_once_with(local=pytest.helpers.anyvar(int))
    print_mock.assert_called_once_with(verbose=False)
