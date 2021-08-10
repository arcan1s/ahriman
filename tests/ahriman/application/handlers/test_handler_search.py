import argparse
import aur

from pytest_mock import MockerFixture

from ahriman.application.handlers import Search
from ahriman.core.configuration import Configuration


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases
    :param args: command line arguments fixture
    :return: generated arguments for these test cases
    """
    args.search = ["ahriman"]
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, aur_package_ahriman: aur.Package,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("aur.search", return_value=[aur_package_ahriman])
    log_mock = mocker.patch("ahriman.application.handlers.search.Search.log_fn")

    Search.run(args, "x86_64", configuration)
    log_mock.assert_called_once()


def test_run_multiple_search(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command with multiple search arguments
    """
    args = _default_args(args)
    args.search = ["ahriman", "is", "cool"]
    search_mock = mocker.patch("aur.search")

    Search.run(args, "x86_64", configuration)
    search_mock.assert_called_with(" ".join(args.search))


def test_log_fn(args: argparse.Namespace, configuration: Configuration, aur_package_ahriman: aur.Package,
                mocker: MockerFixture) -> None:
    """
    log function must call print built-in
    """
    args = _default_args(args)
    mocker.patch("aur.search", return_value=[aur_package_ahriman])
    print_mock = mocker.patch("builtins.print")

    Search.run(args, "x86_64", configuration)
    print_mock.assert_called()  # we don't really care about call details tbh
