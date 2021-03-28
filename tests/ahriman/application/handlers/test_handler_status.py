import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Status
from ahriman.core.configuration import Configuration


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args.ahriman = True
    args.package = []
    args.without_dependencies = False
    mocker.patch("pathlib.Path.mkdir")
    application_mock = mocker.patch("ahriman.core.status.client.Client.get_self")
    packages_mock = mocker.patch("ahriman.core.status.client.Client.get")

    Status.run(args, "x86_64", configuration)
    application_mock.assert_called_once()
    packages_mock.assert_called_once()
