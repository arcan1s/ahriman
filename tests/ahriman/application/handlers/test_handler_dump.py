import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Dump
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")
    application_mock = mocker.patch("ahriman.core.configuration.Configuration.dump",
                                    return_value=configuration.dump())

    Dump.run(args, "x86_64", configuration, report=False, unsafe=False)
    application_mock.assert_called_once_with()
    print_mock.assert_called()


def test_disallow_auto_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Dump.ALLOW_AUTO_ARCHITECTURE_RUN
