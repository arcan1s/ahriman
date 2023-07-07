import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import RemoveUnknown
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
    args.dry_run = False
    return args


def test_run(args: argparse.Namespace, package_ahriman: Package, configuration: Configuration,
             repository: Repository, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    application_mock = mocker.patch("ahriman.application.application.Application.unknown",
                                    return_value=[package_ahriman])
    remove_mock = mocker.patch("ahriman.application.application.Application.remove")
    on_start_mock = mocker.patch("ahriman.application.application.Application.on_start")

    RemoveUnknown.run(args, "x86_64", configuration, report=False)
    application_mock.assert_called_once_with()
    remove_mock.assert_called_once_with([package_ahriman])
    on_start_mock.assert_called_once_with()


def test_run_dry_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                     package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run simplified command
    """
    args = _default_args(args)
    args.dry_run = True
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    application_mock = mocker.patch("ahriman.application.application.Application.unknown",
                                    return_value=[package_ahriman])
    remove_mock = mocker.patch("ahriman.application.application.Application.remove")
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")

    RemoveUnknown.run(args, "x86_64", configuration, report=False)
    application_mock.assert_called_once_with()
    remove_mock.assert_not_called()
    print_mock.assert_called_once_with(verbose=False)
