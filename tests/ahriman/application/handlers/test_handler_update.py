import argparse
import pytest

from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.application.application import Application
from ahriman.application.handlers import Update
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.models.package import Package
from ahriman.models.packagers import Packagers
from ahriman.models.result import Result


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.aur = True
    args.changes = True
    args.check_files = True
    args.package = []
    args.dependencies = True
    args.dry_run = False
    args.exit_code = False
    args.increment = True
    args.local = True
    args.manual = True
    args.refresh = 0
    args.username = "username"
    args.vcs = True
    return args


def test_run(args: argparse.Namespace, package_ahriman: Package, configuration: Configuration, repository: Repository,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    result = Result()
    result.add_updated(package_ahriman)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    application_mock = mocker.patch("ahriman.application.application.Application.update", return_value=result)
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")
    dependencies_mock = mocker.patch("ahriman.application.application.Application.with_dependencies",
                                     return_value=[package_ahriman])
    updates_mock = mocker.patch("ahriman.application.application.Application.updates", return_value=[package_ahriman])
    changes_mock = mocker.patch("ahriman.application.application.Application.changes")
    on_start_mock = mocker.patch("ahriman.application.application.Application.on_start")
    print_mock = mocker.patch("ahriman.application.application.Application.print_updates")

    _, repository_id = configuration.check_loaded()
    Update.run(args, repository_id, configuration, report=False)
    application_mock.assert_called_once_with([package_ahriman],
                                             Packagers(args.username, {package_ahriman.base: "packager"}),
                                             bump_pkgrel=args.increment)
    updates_mock.assert_called_once_with(
        args.package, aur=args.aur, local=args.local, manual=args.manual, vcs=args.vcs, check_files=args.check_files)
    changes_mock.assert_not_called()
    dependencies_mock.assert_called_once_with([package_ahriman], process_dependencies=args.dependencies)
    check_mock.assert_called_once_with(False, False)
    on_start_mock.assert_called_once_with()
    print_mock.assert_called_once_with([package_ahriman], log_fn=pytest.helpers.anyvar(int))


def test_run_empty_exception(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                             mocker: MockerFixture) -> None:
    """
    must raise ExitCode exception on empty update list
    """
    args = _default_args(args)
    args.exit_code = True
    args.dry_run = True
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.application.application.Application.updates", return_value=[])
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")

    _, repository_id = configuration.check_loaded()
    Update.run(args, repository_id, configuration, report=False)
    check_mock.assert_called_once_with(True, True)


def test_run_update_empty_exception(args: argparse.Namespace, package_ahriman: Package, configuration: Configuration,
                                    repository: Repository, mocker: MockerFixture) -> None:
    """
    must raise ExitCode exception on empty build result
    """
    args = _default_args(args)
    args.exit_code = True
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.application.application.Application.update", return_value=Result())
    mocker.patch("ahriman.application.application.Application.updates", return_value=[package_ahriman])
    mocker.patch("ahriman.application.application.Application.with_dependencies", return_value=[package_ahriman])
    mocker.patch("ahriman.application.application.Application.print_updates")
    changes_mock = mocker.patch("ahriman.application.application.Application.changes")
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")

    _, repository_id = configuration.check_loaded()
    Update.run(args, repository_id, configuration, report=False)
    changes_mock.assert_not_called()
    check_mock.assert_called_once_with(True, True)


def test_run_dry_run(args: argparse.Namespace, package_ahriman: Package, configuration: Configuration,
                     repository: Repository, mocker: MockerFixture) -> None:
    """
    must run simplified command
    """
    args = _default_args(args)
    args.dry_run = True
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    application_mock = mocker.patch("ahriman.application.application.Application.update")
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")
    updates_mock = mocker.patch("ahriman.application.application.Application.updates", return_value=[package_ahriman])
    changes_mock = mocker.patch("ahriman.application.application.Application.changes")

    _, repository_id = configuration.check_loaded()
    Update.run(args, repository_id, configuration, report=False)
    updates_mock.assert_called_once_with(
        args.package, aur=args.aur, local=args.local, manual=args.manual, vcs=args.vcs, check_files=args.check_files)
    application_mock.assert_not_called()
    changes_mock.assert_called_once_with([package_ahriman])
    check_mock.assert_called_once_with(False, pytest.helpers.anyvar(int))


def test_run_no_changes(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                        mocker: MockerFixture) -> None:
    """
    must skip changes calculation
    """
    args = _default_args(args)
    args.dry_run = True
    args.changes = False
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.application.application.Application.update")
    mocker.patch("ahriman.application.handlers.Handler.check_if_empty")
    mocker.patch("ahriman.application.application.Application.updates")
    changes_mock = mocker.patch("ahriman.application.application.Application.changes")

    _, repository_id = configuration.check_loaded()
    Update.run(args, repository_id, configuration, report=False)
    changes_mock.assert_not_called()


def test_log_fn(application: Application, mocker: MockerFixture) -> None:
    """
    must print package updates
    """
    logger_mock = mocker.patch("logging.Logger.info")
    Update.log_fn(application, False)("hello")
    logger_mock.assert_has_calls([MockCall("hello")])
