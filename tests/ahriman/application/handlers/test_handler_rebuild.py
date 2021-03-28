import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Rebuild
from ahriman.core.configuration import Configuration


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    mocker.patch("pathlib.Path.mkdir")
    application_packages_mock = mocker.patch("ahriman.core.repository.repository.Repository.packages")
    application_mock = mocker.patch("ahriman.application.application.Application.update")

    Rebuild.run(args, "x86_64", configuration)
    application_packages_mock.assert_called_once()
    application_mock.assert_called_once()
