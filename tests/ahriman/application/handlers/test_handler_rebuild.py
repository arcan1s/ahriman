import argparse
import pytest

from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.application.application import Application
from ahriman.application.handlers import Rebuild
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
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
    args.depends_on = []
    args.dry_run = False
    args.from_database = False
    args.exit_code = False
    return args


def test_run(args: argparse.Namespace, package_ahriman: Package, configuration: Configuration,
             repository: Repository, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    result = Result()
    result.add_success(package_ahriman)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    extract_mock = mocker.patch("ahriman.application.handlers.Rebuild.extract_packages", return_value=[package_ahriman])
    application_packages_mock = mocker.patch("ahriman.core.repository.repository.Repository.packages_depend_on",
                                             return_value=[package_ahriman])
    application_mock = mocker.patch("ahriman.application.application.Application.update", return_value=result)
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")
    on_start_mock = mocker.patch("ahriman.application.application.Application.on_start")

    Rebuild.run(args, "x86_64", configuration, report=False, unsafe=False)
    extract_mock.assert_called_once_with(pytest.helpers.anyvar(int), from_database=args.from_database)
    application_packages_mock.assert_called_once_with([package_ahriman], None)
    application_mock.assert_called_once_with([package_ahriman])
    check_mock.assert_has_calls([MockCall(False, False), MockCall(False, False)])
    on_start_mock.assert_called_once_with()


def test_run_extract_packages(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                              mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    args.from_database = True
    args.dry_run = True
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.application.application.Application.add")
    extract_mock = mocker.patch("ahriman.application.handlers.Rebuild.extract_packages", return_value=[])

    Rebuild.run(args, "x86_64", configuration, report=False, unsafe=False)
    extract_mock.assert_called_once_with(pytest.helpers.anyvar(int), from_database=args.from_database)


def test_run_dry_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                     package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run command without update itself
    """
    args = _default_args(args)
    args.dry_run = True
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.application.handlers.Rebuild.extract_packages", return_value=[package_ahriman])
    application_mock = mocker.patch("ahriman.application.application.Application.update")
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")

    Rebuild.run(args, "x86_64", configuration, report=False, unsafe=False)
    application_mock.assert_not_called()
    check_mock.assert_called_once_with(False, False)


def test_run_filter(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                    mocker: MockerFixture) -> None:
    """
    must run command with depends on filter
    """
    args = _default_args(args)
    args.depends_on = ["python-aur"]
    mocker.patch("ahriman.application.application.Application.update")
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.application.handlers.Rebuild.extract_packages", return_value=[])
    application_packages_mock = mocker.patch("ahriman.core.repository.repository.Repository.packages_depend_on")

    Rebuild.run(args, "x86_64", configuration, report=False, unsafe=False)
    application_packages_mock.assert_called_once_with([], {"python-aur"})


def test_run_without_filter(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                            mocker: MockerFixture) -> None:
    """
    must run command for all packages if no filter supplied
    """
    args = _default_args(args)
    mocker.patch("ahriman.application.application.Application.update")
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.application.handlers.Rebuild.extract_packages", return_value=[])
    application_packages_mock = mocker.patch("ahriman.core.repository.repository.Repository.packages_depend_on")

    Rebuild.run(args, "x86_64", configuration, report=False, unsafe=False)
    application_packages_mock.assert_called_once_with([], None)


def test_run_update_empty_exception(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                                    mocker: MockerFixture) -> None:
    """
    must raise ExitCode exception on empty update list
    """
    args = _default_args(args)
    args.exit_code = True
    args.dry_run = True
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.application.handlers.Rebuild.extract_packages")
    mocker.patch("ahriman.core.repository.repository.Repository.packages_depend_on", return_value=[])
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")

    Rebuild.run(args, "x86_64", configuration, report=False, unsafe=False)
    check_mock.assert_called_once_with(True, True)


def test_run_build_empty_exception(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                                   package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must raise ExitCode exception on empty update result
    """
    args = _default_args(args)
    args.exit_code = True
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.application.handlers.Rebuild.extract_packages")
    mocker.patch("ahriman.core.repository.repository.Repository.packages_depend_on", return_value=[package_ahriman])
    mocker.patch("ahriman.application.application.Application.update", return_value=Result())
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")

    Rebuild.run(args, "x86_64", configuration, report=False, unsafe=False)
    check_mock.assert_has_calls([MockCall(True, False), MockCall(True, True)])


def test_extract_packages(application: Application, mocker: MockerFixture) -> None:
    """
    must extract packages from database
    """
    packages_mock = mocker.patch("ahriman.core.repository.repository.Repository.packages")
    Rebuild.extract_packages(application, from_database=False)
    packages_mock.assert_called_once_with()


def test_extract_packages_from_database(application: Application, mocker: MockerFixture) -> None:
    """
    must extract packages from database
    """
    packages_mock = mocker.patch("ahriman.core.database.SQLite.packages_get")
    Rebuild.extract_packages(application, from_database=True)
    packages_mock.assert_called_once_with()
