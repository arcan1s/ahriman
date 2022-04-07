import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.application import Application
from ahriman.application.handlers import Add
from ahriman.core.configuration import Configuration
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.result import Result


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases
    :param args: command line arguments fixture
    :return: generated arguments for these test cases
    """
    args.package = []
    args.exit_code = False
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

    Add.run(args, "x86_64", configuration, True, False)
    application_mock.assert_called_once_with(args.package, args.source, args.without_dependencies)


def test_run_extract_packages(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    args.package = None
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch("ahriman.application.application.Application.add")
    extract_mock = mocker.patch("ahriman.application.handlers.Add.extract_packages", return_value=[])

    Add.run(args, "x86_64", configuration, True, False)
    extract_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_run_with_updates(args: argparse.Namespace, configuration: Configuration,
                          package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run command with updates after
    """
    args = _default_args(args)
    args.now = True
    result = Result()
    result.add_success(package_ahriman)
    mocker.patch("ahriman.application.application.Application.add")
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.application.application.Application.update", return_value=result)
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_if_empty")
    updates_mock = mocker.patch("ahriman.application.application.Application.updates", return_value=[package_ahriman])

    Add.run(args, "x86_64", configuration, True, False)
    updates_mock.assert_called_once_with(args.package, True, True, False, True, pytest.helpers.anyvar(int))
    application_mock.assert_called_once_with([package_ahriman])
    check_mock.assert_called_once_with(False, False)


def test_run_empty_exception(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must raise ExitCode exception on empty result
    """
    args = _default_args(args)
    args.now = True
    args.exit_code = True
    mocker.patch("ahriman.application.application.Application.add")
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch("ahriman.application.application.Application.update", return_value=Result())
    mocker.patch("ahriman.application.application.Application.updates")
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_if_empty")

    Add.run(args, "x86_64", configuration, True, False)
    check_mock.assert_called_once_with(True, True)


def test_extract_packages(application: Application, mocker: MockerFixture) -> None:
    """
    must extract packages from database
    """
    packages_mock = mocker.patch("ahriman.core.database.sqlite.SQLite.packages_get")
    Add.extract_packages(application)
    packages_mock.assert_called_once_with()
