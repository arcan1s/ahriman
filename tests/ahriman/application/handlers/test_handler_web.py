import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Web
from ahriman.core.configuration import Configuration


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    mocker.patch("pathlib.Path.mkdir")
    setup_mock = mocker.patch("ahriman.web.web.setup_service")
    run_mock = mocker.patch("ahriman.web.web.run_server")

    Web.run(args, "x86_64", configuration)
    setup_mock.assert_called_once()
    run_mock.assert_called_once()
