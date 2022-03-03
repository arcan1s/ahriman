import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.handlers import Add
from ahriman.core.configuration import Configuration
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases
    :param args: command line arguments fixture
    :return: generated arguments for these test cases
    """
    args.package = []
    args.now = False
    args.source = PackageSource.Auto
    args.without_dependencies = False
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.application.application.Application.add")

    Add.run(args, "x86_64", configuration, True)
    application_mock.assert_called_once_with(args.package, args.source, args.without_dependencies)


def test_run_with_updates(args: argparse.Namespace, configuration: Configuration,
                          package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run command with updates after
    """
    args = _default_args(args)
    args.now = True
    mocker.patch("ahriman.application.application.Application.add")
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.application.application.Application.update")
    updates_mock = mocker.patch("ahriman.application.application.Application.updates", return_value=[package_ahriman])

    Add.run(args, "x86_64", configuration, True)
    updates_mock.assert_called_once_with(args.package, True, True, False, True, pytest.helpers.anyvar(int))
    application_mock.assert_called_once_with([package_ahriman])
