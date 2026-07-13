import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.handlers.hold import Hold
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.models.action import Action


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.package = ["ahriman"]
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    args.action = Action.Update
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    hold_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_hold_update")

    _, repository_id = configuration.check_loaded()
    Hold.run(args, repository_id, configuration, report=False)
    hold_mock.assert_called_once_with("ahriman", enabled=True)


def test_run_remove(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                    mocker: MockerFixture) -> None:
    """
    must remove held status
    """
    args = _default_args(args)
    args.action = Action.Remove
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    hold_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_hold_update")

    _, repository_id = configuration.check_loaded()
    Hold.run(args, repository_id, configuration, report=False)
    hold_mock.assert_called_once_with("ahriman", enabled=False)
