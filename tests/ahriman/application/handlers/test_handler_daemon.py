import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Daemon
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
    args.interval = 60 * 60 * 12
    args.partitions = True
    args.refresh = 0
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, package_ahriman: Package, repository: Repository,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    run_mock = mocker.patch("ahriman.application.handlers.Update.run")
    iter_mock = mocker.patch("ahriman.application.application.updates_iterator.UpdatesIterator.__iter__",
                             return_value=iter([[package_ahriman.base]]))

    _, repository_id = configuration.check_loaded()
    Daemon.run(args, repository_id, configuration, report=True)
    args.package = [package_ahriman.base]
    run_mock.assert_called_once_with(args, repository_id, configuration, report=True)
    iter_mock.assert_called_once_with()


def test_run_no_partitions(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                           mocker: MockerFixture) -> None:
    """
    must run command without partitioning
    """
    args = _default_args(args)
    args.partitions = False
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    run_mock = mocker.patch("ahriman.application.handlers.Update.run")
    iter_mock = mocker.patch("ahriman.application.application.updates_iterator.UpdatesIterator.__iter__",
                             return_value=iter([[]]))

    _, repository_id = configuration.check_loaded()
    Daemon.run(args, repository_id, configuration, report=True)
    run_mock.assert_called_once_with(args, repository_id, configuration, report=True)
    iter_mock.assert_called_once_with()


def test_run_no_updates(args: argparse.Namespace, configuration: Configuration, package_ahriman: Package,
                        repository: Repository, mocker: MockerFixture) -> None:
    """
    must skip empty update list
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    run_mock = mocker.patch("ahriman.application.handlers.Update.run")
    iter_mock = mocker.patch("ahriman.application.application.updates_iterator.UpdatesIterator.__iter__",
                             return_value=iter([[package_ahriman.base], None]))

    _, repository_id = configuration.check_loaded()
    Daemon.run(args, repository_id, configuration, report=True)
    args.package = [package_ahriman.base]
    run_mock.assert_called_once_with(args, repository_id, configuration, report=True)
    iter_mock.assert_called_once_with()
