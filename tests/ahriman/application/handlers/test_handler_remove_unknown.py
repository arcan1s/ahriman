import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import RemoveUnknown
from ahriman.core.configuration import Configuration
from ahriman.models.package import Package


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases
    :param args: command line arguments fixture
    :return: generated arguments for these test cases
    """
    args.dry_run = False
    args.info = False
    return args


def test_run(args: argparse.Namespace, package_ahriman: Package,
             configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.application.application.Application.unknown",
                                    return_value=[package_ahriman])
    remove_mock = mocker.patch("ahriman.application.application.Application.remove")

    RemoveUnknown.run(args, "x86_64", configuration, True, False)
    application_mock.assert_called_once_with()
    remove_mock.assert_called_once_with([package_ahriman])


def test_run_dry_run(args: argparse.Namespace, configuration: Configuration, package_ahriman: Package,
                     mocker: MockerFixture) -> None:
    """
    must run simplified command
    """
    args = _default_args(args)
    args.dry_run = True
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.application.application.Application.unknown",
                                    return_value=[package_ahriman])
    remove_mock = mocker.patch("ahriman.application.application.Application.remove")
    print_mock = mocker.patch("ahriman.application.formatters.printer.Printer.print")

    RemoveUnknown.run(args, "x86_64", configuration, True, False)
    application_mock.assert_called_once_with()
    remove_mock.assert_not_called()
    print_mock.assert_called_once_with(False)


def test_run_dry_run_verbose(args: argparse.Namespace, configuration: Configuration, package_ahriman: Package,
                             mocker: MockerFixture) -> None:
    """
    must run simplified command with increased verbosity
    """
    args = _default_args(args)
    args.dry_run = True
    args.info = True
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.application.application.Application.unknown",
                                    return_value=[package_ahriman])
    remove_mock = mocker.patch("ahriman.application.application.Application.remove")
    print_mock = mocker.patch("ahriman.application.formatters.printer.Printer.print")

    RemoveUnknown.run(args, "x86_64", configuration, True, False)
    application_mock.assert_called_once_with()
    remove_mock.assert_not_called()
    print_mock.assert_called_once_with(True)
