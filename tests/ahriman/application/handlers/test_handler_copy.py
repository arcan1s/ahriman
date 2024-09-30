import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.application import Application
from ahriman.application.handlers.copy import Copy
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.source = "source"
    args.package = ["ahriman"]
    args.exit_code = False
    args.remove = False
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.core.repository.Repository.packages", return_value=[package_ahriman])
    application_mock = mocker.patch("ahriman.application.handlers.copy.Copy.copy_package")
    update_mock = mocker.patch("ahriman.application.application.Application.update")
    remove_mock = mocker.patch("ahriman.application.application.Application.remove")
    on_start_mock = mocker.patch("ahriman.application.application.Application.on_start")

    _, repository_id = configuration.check_loaded()
    Copy.run(args, repository_id, configuration, report=False)
    application_mock.assert_called_once_with(package_ahriman, pytest.helpers.anyvar(int), pytest.helpers.anyvar(int))
    update_mock.assert_called_once_with([])
    remove_mock.assert_not_called()
    on_start_mock.assert_called_once_with()


def test_run_remove(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                    package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run command and remove packages afterwards
    """
    args = _default_args(args)
    args.remove = True
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.core.repository.Repository.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.application.handlers.copy.Copy.copy_package")
    mocker.patch("ahriman.application.application.Application.update")
    remove_mock = mocker.patch("ahriman.application.application.Application.remove")

    _, repository_id = configuration.check_loaded()
    Copy.run(args, repository_id, configuration, report=False)
    remove_mock.assert_called_once_with(args.package)


def test_run_empty_exception(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                             mocker: MockerFixture) -> None:
    """
    must raise ExitCode exception on empty result
    """
    args = _default_args(args)
    args.exit_code = True
    mocker.patch("ahriman.core.repository.Repository.packages", return_value=[])
    mocker.patch("ahriman.application.application.Application.update")
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_status")

    _, repository_id = configuration.check_loaded()
    Copy.run(args, repository_id, configuration, report=False)
    check_mock.assert_called_once_with(True, [])


def test_copy_package(package_ahriman: Package, application: Application, mocker: MockerFixture) -> None:
    """
    must copy package between repositories and its metadata
    """
    add_mock = mocker.patch("ahriman.application.application.Application.add")
    changes_get_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_changes_get")
    changes_update_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_changes_update")
    deps_get_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_dependencies_get")
    deps_update_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_dependencies_update")
    package_update_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_update")
    path = application.repository.paths.repository / package_ahriman.packages[package_ahriman.base].filename

    Copy.copy_package(package_ahriman, application, application)
    add_mock.assert_called_once_with([str(path)], PackageSource.Archive)
    changes_get_mock.assert_called_once_with(package_ahriman.base)
    changes_update_mock.assert_called_once_with(package_ahriman.base, changes_get_mock.return_value)
    deps_get_mock.assert_called_once_with(package_ahriman.base)
    deps_update_mock.assert_called_once_with(package_ahriman.base, deps_get_mock.return_value)
    package_update_mock.assert_called_once_with(package_ahriman, BuildStatusEnum.Pending)
