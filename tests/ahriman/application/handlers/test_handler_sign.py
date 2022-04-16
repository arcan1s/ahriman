import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Sign
from ahriman.core.configuration import Configuration


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
      args(argparse.Namespace): command line arguments fixture

    Returns:
      argparse.Namespace: generated arguments for these test cases
    """
    args.package = []
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.application.application.Application.sign")

    Sign.run(args, "x86_64", configuration, True, False)
    application_mock.assert_called_once_with([])
