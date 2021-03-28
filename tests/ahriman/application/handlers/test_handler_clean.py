import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Clean
from ahriman.core.configuration import Configuration


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args.no_build = False
    args.no_cache = False
    args.no_chroot = False
    args.no_manual = False
    args.no_packages = False
    mocker.patch("pathlib.Path.mkdir")
    application_mock = mocker.patch("ahriman.application.application.Application.clean")

    Clean.run(args, "x86_64", configuration)
    application_mock.assert_called_once()
