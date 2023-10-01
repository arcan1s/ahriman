import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman import __version__
from ahriman.application.handlers import ServiceUpdates
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
    args.exit_code = False
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run command
    """
    package_ahriman.version = "0.0.0-1"
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    package_mock = mocker.patch("ahriman.models.package.Package.from_aur", return_value=package_ahriman)
    application_mock = mocker.patch("ahriman.core.formatters.Printer.print")
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")

    _, repository_id = configuration.check_loaded()
    ServiceUpdates.run(args, repository_id, configuration, report=False)
    package_mock.assert_called_once_with(package_ahriman.base, repository.pacman, None)
    application_mock.assert_called_once_with(verbose=True, log_fn=pytest.helpers.anyvar(int), separator=" -> ")
    check_mock.assert_called_once_with(args.exit_code, True)


def test_run_skip(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                  package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must do not perform any actions if package is up-to-date
    """
    package_ahriman.version = f"{__version__}-1"
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.models.package.Package.from_aur", return_value=package_ahriman)
    application_mock = mocker.patch("ahriman.core.formatters.Printer.print")
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")

    _, repository_id = configuration.check_loaded()
    ServiceUpdates.run(args, repository_id, configuration, report=False)
    application_mock.assert_not_called()
    check_mock.assert_not_called()


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not ServiceUpdates.ALLOW_MULTI_ARCHITECTURE_RUN
