import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Web
from ahriman.core.configuration import Configuration


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases
    :param args: command line arguments fixture
    :return: generated arguments for these test cases
    """
    args.parser = lambda: True
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.mkdir")
    mocker.patch("ahriman.core.spawn.Spawn.start")
    setup_mock = mocker.patch("ahriman.web.web.setup_service")
    run_mock = mocker.patch("ahriman.web.web.run_server")

    Web.run(args, "x86_64", configuration, True)
    setup_mock.assert_called_once()
    run_mock.assert_called_once()
