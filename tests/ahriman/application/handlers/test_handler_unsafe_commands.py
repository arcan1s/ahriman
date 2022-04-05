import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.ahriman import _parser
from ahriman.application.handlers import UnsafeCommands
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import ExitCode


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases
    :param args: command line arguments fixture
    :return: generated arguments for these test cases
    """
    args.parser = _parser
    args.command = None
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    commands_mock = mocker.patch("ahriman.application.handlers.UnsafeCommands.get_unsafe_commands",
                                 return_value=["command"])
    print_mock = mocker.patch("ahriman.core.formatters.printer.Printer.print")

    UnsafeCommands.run(args, "x86_64", configuration, True, False)
    commands_mock.assert_called_once_with(pytest.helpers.anyvar(int))
    print_mock.assert_called_once_with(verbose=True)


def test_run_check(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command and check if command is unsafe
    """
    args = _default_args(args)
    args.command = "clean"
    commands_mock = mocker.patch("ahriman.application.handlers.UnsafeCommands.get_unsafe_commands",
                                 return_value=["command"])
    check_mock = mocker.patch("ahriman.application.handlers.UnsafeCommands.check_unsafe")

    UnsafeCommands.run(args, "x86_64", configuration, True, False)
    commands_mock.assert_called_once_with(pytest.helpers.anyvar(int))
    check_mock.assert_called_once_with("clean", ["command"], pytest.helpers.anyvar(int))


def test_check_unsafe() -> None:
    """
    must check if command is unsafe
    """
    with pytest.raises(ExitCode):
        UnsafeCommands.check_unsafe("repo-clean", ["repo-clean"], _parser())


def test_check_unsafe_safe() -> None:
    """
    must check if command is safe
    """
    UnsafeCommands.check_unsafe("package-status", ["repo-clean"], _parser())


def test_get_unsafe_commands() -> None:
    """
    must return unsafe commands
    """
    parser = _parser()
    subparser = next(action for action in parser._actions if isinstance(action, argparse._SubParsersAction))
    commands = UnsafeCommands.get_unsafe_commands(parser)
    for command in commands:
        assert subparser.choices[command].get_default("unsafe")


def test_disallow_auto_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not UnsafeCommands.ALLOW_AUTO_ARCHITECTURE_RUN
