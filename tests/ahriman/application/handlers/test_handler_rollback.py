import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.application import Application
from ahriman.application.handlers.rollback import Rollback
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import UnknownPackageError
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
    args.package = "ahriman"
    args.version = "1.0.0-1"
    args.hold = False
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository, package_ahriman: Package,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    artifacts = [package.filepath for package in package_ahriman.packages.values()]
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    on_start_mock = mocker.patch("ahriman.application.application.Application.on_start")
    load_mock = mocker.patch("ahriman.application.handlers.rollback.Rollback.package_load",
                             return_value=package_ahriman)
    artifacts_mock = mocker.patch("ahriman.application.handlers.rollback.Rollback.package_artifacts",
                                  return_value=artifacts)
    perform_mock = mocker.patch("ahriman.application.handlers.add.Add.perform_action")
    hold_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_hold_update")

    _, repository_id = configuration.check_loaded()
    Rollback.run(args, repository_id, configuration, report=False)
    on_start_mock.assert_called_once_with()
    load_mock.assert_called_once_with(pytest.helpers.anyvar(int), package_ahriman.base, args.version)
    artifacts_mock.assert_called_once_with(pytest.helpers.anyvar(int), package_ahriman)
    perform_mock.assert_called_once_with(pytest.helpers.anyvar(int), args)
    hold_mock.assert_not_called()


def test_run_hold(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                  package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must hold package after rollback
    """
    args = _default_args(args)
    args.hold = True
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.application.application.Application.on_start")
    mocker.patch("ahriman.application.handlers.rollback.Rollback.package_load", return_value=package_ahriman)
    mocker.patch("ahriman.application.handlers.rollback.Rollback.package_artifacts", return_value=[])
    mocker.patch("ahriman.application.handlers.add.Add.perform_action")
    hold_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_hold_update")

    _, repository_id = configuration.check_loaded()
    Rollback.run(args, repository_id, configuration, report=False)
    hold_mock.assert_called_once_with(package_ahriman.base, enabled=True)


def test_package_artifacts(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return package artifacts
    """
    artifacts = [package.filepath for package in package_ahriman.packages.values()]
    lookup_mock = mocker.patch("ahriman.core.repository.Repository.package_archives_lookup", return_value=artifacts)

    assert Rollback.package_artifacts(application, package_ahriman) == artifacts
    lookup_mock.assert_called_once_with(package_ahriman)


def test_package_artifacts_empty(application: Application, package_ahriman: Package,
                                 mocker: MockerFixture) -> None:
    """
    must raise UnknownPackageError if no artifacts found
    """
    mocker.patch("ahriman.core.repository.Repository.package_archives_lookup", return_value=[])
    with pytest.raises(UnknownPackageError):
        Rollback.package_artifacts(application, package_ahriman)


def test_package_load(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must load package from reporter
    """
    package_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_get",
                                return_value=[(package_ahriman, None)])

    result = Rollback.package_load(application, package_ahriman.base, "2.0.0-1")
    assert result.version == "2.0.0-1"
    package_mock.assert_called_once_with(package_ahriman.base)


def test_package_load_unknown(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must raise UnknownPackageError if package not found
    """
    mocker.patch("ahriman.core.status.local_client.LocalClient.package_get", return_value=[])
    with pytest.raises(UnknownPackageError):
        Rollback.package_load(application, package_ahriman.base, package_ahriman.version)
