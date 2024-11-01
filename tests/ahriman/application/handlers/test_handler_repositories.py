import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.handlers.repositories import Repositories
from ahriman.core.configuration import Configuration


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.configuration = None  # doesn't matter actually
    args.id_only = False
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")
    _, repository_id = configuration.check_loaded()
    application_mock = mocker.patch("ahriman.application.handlers.handler.Handler.repositories_extract",
                                    return_value=[repository_id])

    Repositories.run(args, repository_id, configuration, report=False)
    application_mock.assert_called_once_with(pytest.helpers.anyvar(int))
    print_mock.assert_called_once_with(verbose=not args.id_only, log_fn=pytest.helpers.anyvar(int), separator=": ")
