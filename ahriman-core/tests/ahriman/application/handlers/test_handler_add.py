import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.application import Application
from ahriman.application.handlers.add import Add
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.models.package_source import PackageSource
from ahriman.models.pkgbuild_patch import PkgbuildPatch


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.package = ["ahriman"]
    args.now = False
    args.refresh = 0
    args.source = PackageSource.Auto
    args.username = "username"
    args.variable = None
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    on_start_mock = mocker.patch("ahriman.application.application.Application.on_start")
    perform_mock = mocker.patch("ahriman.application.handlers.add.Add.perform_action")

    _, repository_id = configuration.check_loaded()
    Add.run(args, repository_id, configuration, report=False)
    on_start_mock.assert_called_once_with()
    perform_mock.assert_called_once_with(pytest.helpers.anyvar(int), args)


def test_perform_action(args: argparse.Namespace, application: Application, mocker: MockerFixture) -> None:
    """
    must perform add action
    """
    args = _default_args(args)
    application_mock = mocker.patch("ahriman.application.application.Application.add")
    update_mock = mocker.patch("ahriman.application.handlers.update.Update.perform_action")

    Add.perform_action(application, args)
    application_mock.assert_called_once_with(args.package, args.source, args.username)
    update_mock.assert_not_called()


def test_perform_action_with_patches(args: argparse.Namespace, application: Application, mocker: MockerFixture) -> None:
    """
    must perform add action and insert temporary patches
    """
    args = _default_args(args)
    args.variable = ["KEY=VALUE"]
    mocker.patch("ahriman.application.application.Application.add")
    patches_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_patches_update")

    Add.perform_action(application, args)
    patches_mock.assert_called_once_with(args.package[0], PkgbuildPatch("KEY", "VALUE"))


def test_perform_action_with_updates(args: argparse.Namespace, application: Application, mocker: MockerFixture) -> None:
    """
    must perform add action with updates after
    """
    args = _default_args(args)
    args.now = True
    mocker.patch("ahriman.application.application.Application.add")
    update_mock = mocker.patch("ahriman.application.handlers.update.Update.perform_action")

    Add.perform_action(application, args)
    update_mock.assert_called_once_with(application, args)
