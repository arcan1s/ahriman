import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Dump
from ahriman.core.configuration import Configuration


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    mocker.patch("pathlib.Path.mkdir")
    print_mock = mocker.patch("ahriman.application.handlers.dump.Dump._print")
    application_mock = mocker.patch("ahriman.core.configuration.Configuration.dump",
                                    return_value=configuration.dump("x86_64"))

    Dump.run(args, "x86_64", configuration)
    application_mock.assert_called_once()
    print_mock.assert_called()
