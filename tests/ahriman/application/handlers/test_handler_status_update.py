import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers.status_update import StatusUpdate
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.repository import Repository
from ahriman.models.action import Action
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.package = None
    args.action = Action.Update
    args.status = BuildStatusEnum.Success
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    update_self_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.status_update")

    _, repository_id = configuration.check_loaded()
    StatusUpdate.run(args, repository_id, configuration, report=False)
    update_self_mock.assert_called_once_with(args.status)


def test_run_packages(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                      mocker: MockerFixture) -> None:
    """
    must run command with specified packages
    """
    args = _default_args(args)
    args.package = ["package"]
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    update_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_status_update")

    _, repository_id = configuration.check_loaded()
    StatusUpdate.run(args, repository_id, configuration, report=False)
    update_mock.assert_called_once_with("package", args.status)


def test_run_remove(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                    package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package from status page
    """
    args = _default_args(args)
    args.package = [package_ahriman.base]
    args.action = Action.Remove
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    update_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_remove")

    _, repository_id = configuration.check_loaded()
    StatusUpdate.run(args, repository_id, configuration, report=False)
    update_mock.assert_called_once_with(package_ahriman.base)


def test_imply_with_report(args: argparse.Namespace, configuration: Configuration, database: SQLite,
                           mocker: MockerFixture) -> None:
    """
    must create application object with native reporting
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    load_mock = mocker.patch("ahriman.core.repository.Repository.load")

    _, repository_id = configuration.check_loaded()
    StatusUpdate.run(args, repository_id, configuration, report=False)
    load_mock.assert_called_once_with(repository_id, configuration, database, report=True, refresh_pacman_database=0)


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not StatusUpdate.ALLOW_MULTI_ARCHITECTURE_RUN
