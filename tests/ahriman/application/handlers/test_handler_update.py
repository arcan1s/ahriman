import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Update
from ahriman.core.configuration import Configuration


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args.package = []
    args.dry_run = False
    args.no_aur = False
    args.no_manual = False
    args.no_vcs = False
    mocker.patch("pathlib.Path.mkdir")
    application_mock = mocker.patch("ahriman.application.application.Application.update")
    updates_mock = mocker.patch("ahriman.application.application.Application.get_updates")

    Update.run(args, "x86_64", configuration)
    application_mock.assert_called_once()
    updates_mock.assert_called_once()


def test_run_dry_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run simplified command
    """
    args.package = []
    args.dry_run = True
    args.no_aur = False
    args.no_manual = False
    args.no_vcs = False
    mocker.patch("pathlib.Path.mkdir")
    updates_mock = mocker.patch("ahriman.application.application.Application.get_updates")

    Update.run(args, "x86_64", configuration)
    updates_mock.assert_called_once()