import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Sign
from ahriman.core.configuration import Configuration


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args.package = []
    mocker.patch("pathlib.Path.mkdir")
    application_mock = mocker.patch("ahriman.application.application.Application.sign")

    Sign.run(args, "x86_64", configuration)
    application_mock.assert_called_once()
