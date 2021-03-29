import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Sync
from ahriman.core.configuration import Configuration


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    args.target = []
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.mkdir")
    application_mock = mocker.patch("ahriman.application.application.Application.sync")

    Sync.run(args, "x86_64", configuration)
    application_mock.assert_called_once()
