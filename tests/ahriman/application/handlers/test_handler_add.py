import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Add
from ahriman.core.configuration import Configuration


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases
    :param args: command line arguments fixture
    :return: generated arguments for these test cases
    """
    args.package = []
    args.now = False
    args.without_dependencies = False
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.mkdir")
    application_mock = mocker.patch("ahriman.application.application.Application.add")

    Add.run(args, "x86_64", configuration, True)
    application_mock.assert_called_once()


def test_run_with_updates(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command with updates after
    """
    args = _default_args(args)
    args.now = True
    mocker.patch("pathlib.Path.mkdir")
    mocker.patch("ahriman.application.application.Application.add")
    application_mock = mocker.patch("ahriman.application.application.Application.update")
    updates_mock = mocker.patch("ahriman.application.application.Application.get_updates")

    Add.run(args, "x86_64", configuration, True)
    application_mock.assert_called_once()
    updates_mock.assert_called_once()
