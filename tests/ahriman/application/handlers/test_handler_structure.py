import argparse
import pytest

from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.application.handlers import Structure
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.models.package import Package


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.partitions = 1
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.core.repository.Repository.packages", return_value=[package_ahriman])
    packages_mock = mocker.patch("ahriman.core.tree.Tree.partition", return_value=[[package_ahriman]])
    application_mock = mocker.patch("ahriman.core.tree.Tree.resolve", return_value=[[package_ahriman]])
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")

    _, repository_id = configuration.check_loaded()
    Structure.run(args, repository_id, configuration, report=False)
    packages_mock.assert_called_once_with([package_ahriman], count=args.partitions)
    application_mock.assert_called_once_with([package_ahriman])
    print_mock.assert_has_calls([
        MockCall(verbose=False, log_fn=pytest.helpers.anyvar(int), separator=": "),
        MockCall(verbose=True, log_fn=pytest.helpers.anyvar(int), separator=" "),
        MockCall(verbose=False, log_fn=pytest.helpers.anyvar(int), separator=": "),
    ])


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Structure.ALLOW_MULTI_ARCHITECTURE_RUN
