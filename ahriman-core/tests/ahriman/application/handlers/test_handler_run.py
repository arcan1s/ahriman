import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.ahriman import _parser
from ahriman.application.handlers.run import Run
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import ExitCode


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.command = ["help"]
    args.parser = _parser
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    application_mock = mocker.patch("ahriman.application.handlers.run.Run.run_command")

    _, repository_id = configuration.check_loaded()
    Run.run(args, repository_id, configuration, report=False)
    application_mock.assert_called_once_with(["help"], pytest.helpers.anyvar(int))


def test_run_failed(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run commands until success
    """
    args = _default_args(args)
    args.command = ["help", "config"]
    application_mock = mocker.patch("ahriman.application.handlers.run.Run.run_command", return_value=False)

    _, repository_id = configuration.check_loaded()
    with pytest.raises(ExitCode):
        Run.run(args, repository_id, configuration, report=False)
    application_mock.assert_called_once_with(["help"], pytest.helpers.anyvar(int))


def test_run_command(mocker: MockerFixture) -> None:
    """
    must correctly run external command
    """
    # because of dynamic load we need to patch exact instance of the object
    parser = _parser()
    subparser = next((action for action in parser._actions if isinstance(action, argparse._SubParsersAction)), None)
    action = subparser.choices["help"]
    execute_mock = mocker.patch.object(action.get_default("handler"), "execute")

    Run.run_command(["help"], parser)
    execute_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Run.ALLOW_MULTI_ARCHITECTURE_RUN
