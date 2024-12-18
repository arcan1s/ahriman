import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.ahriman import _parser
from ahriman.application.handlers.unsafe_commands import UnsafeCommands
from ahriman.core.configuration import Configuration


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.parser = _parser
    args.subcommand = []
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    commands_mock = mocker.patch("ahriman.application.handlers.unsafe_commands.UnsafeCommands.get_unsafe_commands",
                                 return_value=["command"])
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")

    _, repository_id = configuration.check_loaded()
    UnsafeCommands.run(args, repository_id, configuration, report=False)
    commands_mock.assert_called_once_with(pytest.helpers.anyvar(int))
    print_mock.assert_called_once_with(verbose=True, log_fn=pytest.helpers.anyvar(int), separator=": ")


def test_run_check(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command and check if command is unsafe
    """
    args = _default_args(args)
    args.subcommand = ["clean"]
    commands_mock = mocker.patch("ahriman.application.handlers.unsafe_commands.UnsafeCommands.get_unsafe_commands",
                                 return_value=["command"])
    check_mock = mocker.patch("ahriman.application.handlers.unsafe_commands.UnsafeCommands.check_unsafe")

    _, repository_id = configuration.check_loaded()
    UnsafeCommands.run(args, repository_id, configuration, report=False)
    commands_mock.assert_called_once_with(pytest.helpers.anyvar(int))
    check_mock.assert_called_once_with(["clean"], ["command"], pytest.helpers.anyvar(int))


def test_check_unsafe(mocker: MockerFixture) -> None:
    """
    must check if command is unsafe
    """
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_status")
    UnsafeCommands.check_unsafe(["service-clean"], ["service-clean"], _parser())
    check_mock.assert_called_once_with(True, False)


def test_check_unsafe_safe(mocker: MockerFixture) -> None:
    """
    must check if command is safe
    """
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_status")
    UnsafeCommands.check_unsafe(["package-status"], ["service-clean"], _parser())
    check_mock.assert_called_once_with(True, True)


def test_get_unsafe_commands() -> None:
    """
    must return unsafe commands
    """
    parser = _parser()
    subparser = next(action for action in parser._actions if isinstance(action, argparse._SubParsersAction))
    commands = UnsafeCommands.get_unsafe_commands(parser)
    for command in commands:
        assert subparser.choices[command].get_default("unsafe")


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not UnsafeCommands.ALLOW_MULTI_ARCHITECTURE_RUN
