import argparse
import pytest

from pytest_mock import MockerFixture
from unittest import mock

from ahriman.application.handlers import Rebuild
from ahriman.core.configuration import Configuration
from ahriman.models.package import Package
from ahriman.models.result import Result


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases
    :param args: command line arguments fixture
    :return: generated arguments for these test cases
    """
    args.depends_on = []
    args.dry_run = False
    args.exit_code = False
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
    application_packages_mock = mocker.patch("ahriman.core.repository.repository.Repository.packages_depends_on",
                                             return_value=[package_ahriman])
    application_mock = mocker.patch("ahriman.application.application.Application.update", return_value=result)
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_if_empty")

    Rebuild.run(args, "x86_64", configuration, True, False)
    application_packages_mock.assert_called_once_with(None)
    application_mock.assert_called_once_with([package_ahriman])
    check_mock.assert_has_calls([mock.call(False, False), mock.call(False, False)])


def test_run_dry_run(args: argparse.Namespace, configuration: Configuration,
                     package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run command without update itself
    """
    args = _default_args(args)
    args.dry_run = True
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch("ahriman.core.repository.repository.Repository.packages_depends_on", return_value=[package_ahriman])
    application_mock = mocker.patch("ahriman.application.application.Application.update")
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_if_empty")

    Rebuild.run(args, "x86_64", configuration, True, False)
    application_mock.assert_not_called()
    check_mock.assert_called_once_with(False, False)


def test_run_filter(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command with depends on filter
    """
    args = _default_args(args)
    args.depends_on = ["python-aur"]
    mocker.patch("ahriman.application.application.Application.update")
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_packages_mock = mocker.patch("ahriman.core.repository.repository.Repository.packages_depends_on")

    Rebuild.run(args, "x86_64", configuration, True, False)
    application_packages_mock.assert_called_once_with({"python-aur"})


def test_run_without_filter(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command for all packages if no filter supplied
    """
    args = _default_args(args)
    mocker.patch("ahriman.application.application.Application.update")
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_packages_mock = mocker.patch("ahriman.core.repository.repository.Repository.packages_depends_on")

    Rebuild.run(args, "x86_64", configuration, True, False)
    application_packages_mock.assert_called_once_with(None)


def test_run_update_empty_exception(args: argparse.Namespace, configuration: Configuration,
                                    mocker: MockerFixture) -> None:
    """
    must raise ExitCode exception on empty update list
    """
    args = _default_args(args)
    args.exit_code = True
    args.dry_run = True
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch("ahriman.core.repository.repository.Repository.packages_depends_on", return_value=[])
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_if_empty")

    Rebuild.run(args, "x86_64", configuration, True, False)
    check_mock.assert_called_once_with(True, True)


def test_run_build_empty_exception(args: argparse.Namespace, configuration: Configuration,
                                   package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must raise ExitCode exception on empty update result
    """
    args = _default_args(args)
    args.exit_code = True
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch("ahriman.core.repository.repository.Repository.packages_depends_on", return_value=[package_ahriman])
    mocker.patch("ahriman.application.application.Application.update", return_value=Result())
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_if_empty")

    Rebuild.run(args, "x86_64", configuration, True, False)
    check_mock.assert_has_calls([mock.call(True, False), mock.call(True, True)])
