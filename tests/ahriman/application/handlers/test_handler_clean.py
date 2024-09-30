import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers.clean import Clean
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
    args.cache = False
    args.chroot = False
    args.manual = False
    args.packages = False
    args.pacman = False
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    application_mock = mocker.patch("ahriman.application.application.Application.clean")
    on_start_mock = mocker.patch("ahriman.application.application.Application.on_start")

    _, repository_id = configuration.check_loaded()
    Clean.run(args, repository_id, configuration, report=False)
    application_mock.assert_called_once_with(cache=False, chroot=False, manual=False, packages=False, pacman=False)
    on_start_mock.assert_called_once_with()
