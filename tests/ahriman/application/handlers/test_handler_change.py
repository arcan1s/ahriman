import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.handlers import Change
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.repository import Repository
from ahriman.models.action import Action
from ahriman.models.changes import Changes


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.action = Action.List
    args.exit_code = False
    args.package = "package"
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    application_mock = mocker.patch("ahriman.core.status.client.Client.package_changes_get",
                                    return_value=Changes("sha", "change"))
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")

    _, repository_id = configuration.check_loaded()
    Change.run(args, repository_id, configuration, report=False)
    application_mock.assert_called_once_with(args.package)
    check_mock.assert_called_once_with(False, False)
    print_mock.assert_called_once_with(verbose=True, log_fn=pytest.helpers.anyvar(int), separator="")


def test_run_empty_exception(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                             mocker: MockerFixture) -> None:
    """
    must raise ExitCode exception on empty changes result
    """
    args = _default_args(args)
    args.exit_code = True
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.core.status.client.Client.package_changes_get", return_value=Changes())
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")

    _, repository_id = configuration.check_loaded()
    Change.run(args, repository_id, configuration, report=False)
    check_mock.assert_called_once_with(True, True)


def test_run_remove(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                    mocker: MockerFixture) -> None:
    """
    must remove package changes
    """
    args = _default_args(args)
    args.action = Action.Remove
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    update_mock = mocker.patch("ahriman.core.status.client.Client.package_changes_set")

    _, repository_id = configuration.check_loaded()
    Change.run(args, repository_id, configuration, report=False)
    update_mock.assert_called_once_with(args.package, Changes())


def test_imply_with_report(args: argparse.Namespace, configuration: Configuration, database: SQLite,
                           mocker: MockerFixture) -> None:
    """
    must create application object with native reporting
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    load_mock = mocker.patch("ahriman.core.repository.Repository.load")

    _, repository_id = configuration.check_loaded()
    Change.run(args, repository_id, configuration, report=False)
    load_mock.assert_called_once_with(repository_id, configuration, database, report=True, refresh_pacman_database=0)


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Change.ALLOW_MULTI_ARCHITECTURE_RUN
