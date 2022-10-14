import argparse
import pytest

from pytest_mock import MockerFixture
from unittest import mock

from ahriman.application.application import Application
from ahriman.application.handlers import Update
from ahriman.core.configuration import Configuration
from ahriman.models.package import Package
from ahriman.models.result import Result


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.package = []
    args.dry_run = False
    args.exit_code = False
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
    result = Result()
    result.add_success(package_ahriman)
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.application.application.Application.update", return_value=result)
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")
    updates_mock = mocker.patch("ahriman.application.application.Application.updates", return_value=[package_ahriman])
    on_start_mock = mocker.patch("ahriman.application.application.Application.on_start")

    Update.run(args, "x86_64", configuration, True, False)
    application_mock.assert_called_once_with([package_ahriman])
    updates_mock.assert_called_once_with(args.package, args.no_aur, args.no_local, args.no_manual, args.no_vcs,
                                         pytest.helpers.anyvar(int))
    check_mock.assert_has_calls([mock.call(False, False), mock.call(False, False)])
    on_start_mock.assert_called_once_with()


def test_run_empty_exception(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must raise ExitCode exception on empty update list
    """
    args = _default_args(args)
    args.exit_code = True
    args.dry_run = True
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch("ahriman.application.application.Application.updates", return_value=[])
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")

    Update.run(args, "x86_64", configuration, True, False)
    check_mock.assert_called_once_with(True, True)


def test_run_update_empty_exception(args: argparse.Namespace, package_ahriman: Package,
                                    configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must raise ExitCode exception on empty build result
    """
    args = _default_args(args)
    args.exit_code = True
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch("ahriman.application.application.Application.update", return_value=Result())
    mocker.patch("ahriman.application.application.Application.updates", return_value=[package_ahriman])
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")

    Update.run(args, "x86_64", configuration, True, False)
    check_mock.assert_has_calls([mock.call(True, False), mock.call(True, True)])


def test_run_dry_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run simplified command
    """
    args = _default_args(args)
    args.dry_run = True
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.application.application.Application.update")
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")
    updates_mock = mocker.patch("ahriman.application.application.Application.updates")

    Update.run(args, "x86_64", configuration, True, False)
    updates_mock.assert_called_once_with(args.package, args.no_aur, args.no_local, args.no_manual, args.no_vcs,
                                         pytest.helpers.anyvar(int))
    application_mock.assert_not_called()
    check_mock.assert_called_once_with(False, pytest.helpers.anyvar(int))


def test_log_fn(application: Application, mocker: MockerFixture) -> None:
    """
    must print package updates
    """
    logger_mock = mocker.patch("logging.Logger.info")
    Update.log_fn(application, False)("hello")
    logger_mock.assert_called_once_with("hello")
