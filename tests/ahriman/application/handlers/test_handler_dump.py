import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Dump
from ahriman.core.configuration import Configuration


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.secure = True
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
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
