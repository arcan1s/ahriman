import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.handlers import Web
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.models.log_handler import LogHandler


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.parser = lambda: True
    args.force = False
    args.log_handler = None
    args.report = True
    args.quiet = False
    args.unsafe = False
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    setup_mock = mocker.patch("ahriman.web.web.setup_service")
    run_mock = mocker.patch("ahriman.web.web.run_server")
    start_mock = mocker.patch("ahriman.core.spawn.Spawn.start")
    stop_mock = mocker.patch("ahriman.core.spawn.Spawn.stop")
    join_mock = mocker.patch("ahriman.core.spawn.Spawn.join")

    Web.run(args, "x86_64", configuration, report=False, unsafe=False)
    setup_mock.assert_called_once_with("x86_64", configuration, pytest.helpers.anyvar(int))
    run_mock.assert_called_once_with(pytest.helpers.anyvar(int))
    start_mock.assert_called_once_with()
    stop_mock.assert_called_once_with()
    join_mock.assert_called_once_with()


def test_extract_arguments(args: argparse.Namespace, configuration: Configuration):
    """
    must extract correct args
    """
    expected = [
        "--architecture", "x86_64",
        "--configuration", str(configuration.path),
    ]

    probe = _default_args(args)
    assert list(Web.extract_arguments(probe, "x86_64", configuration)) == expected

    probe.force = True
    expected.extend(["--force"])
    assert list(Web.extract_arguments(probe, "x86_64", configuration)) == expected

    probe.log_handler = LogHandler.Console
    expected.extend(["--log-handler", probe.log_handler.value])
    assert list(Web.extract_arguments(probe, "x86_64", configuration)) == expected

    probe.quiet = True
    expected.extend(["--quiet"])
    assert list(Web.extract_arguments(probe, "x86_64", configuration)) == expected

    probe.unsafe = True
    expected.extend(["--unsafe"])
    assert list(Web.extract_arguments(probe, "x86_64", configuration)) == expected


def test_extract_arguments_full(parser: argparse.ArgumentParser, configuration: Configuration):
    """
    must extract all available args except for blacklisted
    """
    # append all options from parser
    args = argparse.Namespace()
    for action in parser._actions:
        if action.default == argparse.SUPPRESS:
            continue
        # extract option from the following list
        value = action.const or \
            next(iter(action.choices or []), None) or \
            (not action.default if isinstance(action.default, bool) else None) or \
            "random string"
        if action.type is not None:
            value = action.type(value)
        setattr(args, action.dest, value)

    assert list(Web.extract_arguments(args, "x86_64", configuration)) == [
        "--architecture", "x86_64",
        "--configuration", str(configuration.path),
        "--force",
        "--log-handler", "console",
        "--quiet",
        "--unsafe",
    ]


def test_disallow_auto_architecture_run() -> None:
    """
    must not allow auto architecture run
    """
    assert not Web.ALLOW_AUTO_ARCHITECTURE_RUN


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Web.ALLOW_MULTI_ARCHITECTURE_RUN
