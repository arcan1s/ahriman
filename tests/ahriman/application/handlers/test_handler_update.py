import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.application import Application
from ahriman.application.handlers import Update
from ahriman.core.configuration import Configuration
from ahriman.models.package import Package


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases
    :param args: command line arguments fixture
    :return: generated arguments for these test cases
    """
    args.package = []
    args.dry_run = False
    args.no_aur = False
    args.no_local = False
    args.no_manual = False
    args.no_vcs = False
    return args


def test_run(args: argparse.Namespace, package_ahriman: Package,
             configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.application.application.Application.update")
    updates_mock = mocker.patch("ahriman.application.application.Application.updates", return_value=[package_ahriman])

    Update.run(args, "x86_64", configuration, True, False)
    application_mock.assert_called_once_with([package_ahriman])
    updates_mock.assert_called_once_with(args.package, args.no_aur, args.no_local, args.no_manual, args.no_vcs,
                                         pytest.helpers.anyvar(int))


def test_run_dry_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run simplified command
    """
    args = _default_args(args)
    args.dry_run = True
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    updates_mock = mocker.patch("ahriman.application.application.Application.updates")

    Update.run(args, "x86_64", configuration, True, False)
    updates_mock.assert_called_once_with(args.package, args.no_aur, args.no_local, args.no_manual, args.no_vcs,
                                         pytest.helpers.anyvar(int))


def test_log_fn(application: Application, mocker: MockerFixture) -> None:
    """
    must print package updates
    """
    logger_mock = mocker.patch("logging.Logger.info")
    Update.log_fn(application, False)("hello")
    logger_mock.assert_called_once_with("hello")
