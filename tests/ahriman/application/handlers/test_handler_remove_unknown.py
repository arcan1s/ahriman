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
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.mkdir")
    application_mock = mocker.patch("ahriman.application.application.Application.unknown")
    remove_mock = mocker.patch("ahriman.application.application.Application.remove")

    RemoveUnknown.run(args, "x86_64", configuration)
    application_mock.assert_called_once()
    remove_mock.assert_called_once()


def test_run_dry_run(args: argparse.Namespace, configuration: Configuration, package_ahriman: Package,
                     mocker: MockerFixture) -> None:
    """
    must run simplified command
    """
    args = _default_args(args)
    args.dry_run = True
    mocker.patch("pathlib.Path.mkdir")
    application_mock = mocker.patch("ahriman.application.application.Application.unknown",
                                    return_value=[package_ahriman])
    remove_mock = mocker.patch("ahriman.application.application.Application.remove")
    log_fn_mock = mocker.patch("ahriman.application.handlers.remove_unknown.RemoveUnknown.log_fn")

    RemoveUnknown.run(args, "x86_64", configuration)
    application_mock.assert_called_once()
    remove_mock.assert_not_called()
    log_fn_mock.assert_called_with(package_ahriman)


def test_log_fn(package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    log function must call print built-in
    """
    print_mock = mocker.patch("builtins.print")

    RemoveUnknown.log_fn(package_ahriman)
    print_mock.assert_called()  # we don't really care about call details tbh
