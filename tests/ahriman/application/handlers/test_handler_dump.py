import argparse
import pytest

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
    args.info = False
    args.key = None
    args.section = None
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

    _, repository_id = configuration.check_loaded()
    Dump.run(args, repository_id, configuration, report=False)
    application_mock.assert_called_once_with()
    print_mock.assert_called()


def test_run_info(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command with info
    """
    args = _default_args(args)
    args.info = True
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")

    _, repository_id = configuration.check_loaded()
    Dump.run(args, repository_id, configuration, report=False)
    print_mock.assert_called()


def test_run_section(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command with filter by section
    """
    args = _default_args(args)
    args.section = "settings"
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")

    _, repository_id = configuration.check_loaded()
    Dump.run(args, repository_id, configuration, report=False)
    print_mock.assert_called_once_with(verbose=False, log_fn=pytest.helpers.anyvar(int), separator=" = ")


def test_run_section_key(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command with filter by section and key
    """
    args = _default_args(args)
    args.section = "settings"
    args.key = "include"
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")
    application_mock = mocker.patch("ahriman.core.configuration.Configuration.dump")

    _, repository_id = configuration.check_loaded()
    Dump.run(args, repository_id, configuration, report=False)
    application_mock.assert_not_called()
    print_mock.assert_called_once_with(verbose=False, log_fn=pytest.helpers.anyvar(int), separator=": ")


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Dump.ALLOW_MULTI_ARCHITECTURE_RUN
