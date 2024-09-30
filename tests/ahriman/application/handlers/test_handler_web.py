import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.handlers.web import Web
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
    args.configuration = None  # doesn't matter actually
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
    setup_mock = mocker.patch("ahriman.web.web.setup_server")
    run_mock = mocker.patch("ahriman.web.web.run_server")
    start_mock = mocker.patch("ahriman.core.spawn.Spawn.start")
    trigger_mock = mocker.patch("ahriman.core.triggers.TriggerLoader.load")
    stop_mock = mocker.patch("ahriman.core.spawn.Spawn.stop")
    join_mock = mocker.patch("ahriman.core.spawn.Spawn.join")
    _, repository_id = configuration.check_loaded()
    mocker.patch("ahriman.application.handlers.handler.Handler.repositories_extract", return_value=[repository_id])

    Web.run(args, repository_id, configuration, report=False)
    setup_mock.assert_called_once_with(configuration, pytest.helpers.anyvar(int), [repository_id])
    run_mock.assert_called_once_with(pytest.helpers.anyvar(int))
    start_mock.assert_called_once_with()
    trigger_mock.assert_called_once_with(repository_id, configuration)
    trigger_mock().on_start.assert_called_once_with()
    stop_mock.assert_called_once_with()
    join_mock.assert_called_once_with()


def test_extract_arguments(args: argparse.Namespace, configuration: Configuration):
    """
    must extract correct args
    """
    expected = [
        "--configuration", str(configuration.path),
    ]

    probe = _default_args(args)
    assert list(Web.extract_arguments(probe, configuration)) == expected

    probe.force = True
    expected.extend(["--force"])
    assert list(Web.extract_arguments(probe, configuration)) == expected

    probe.log_handler = LogHandler.Console
    expected.extend(["--log-handler", probe.log_handler.value])
    assert list(Web.extract_arguments(probe, configuration)) == expected

    probe.quiet = True
    expected.extend(["--quiet"])
    assert list(Web.extract_arguments(probe, configuration)) == expected

    probe.unsafe = True
    expected.extend(["--unsafe"])
    assert list(Web.extract_arguments(probe, configuration)) == expected

    configuration.set_option("web", "wait_timeout", "60")
    expected.extend(["--wait-timeout", "60"])
    assert list(Web.extract_arguments(probe, configuration)) == expected


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
            (42 if action.type == int else None) or \
            "random string"
        if action.type is not None:
            value = action.type(value)
        setattr(args, action.dest, value)

    assert list(Web.extract_arguments(args, configuration)) == [
        "--configuration", str(configuration.path),
        "--force",
        "--log-handler", "console",
        "--quiet",
        "--unsafe",
    ]


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Web.ALLOW_MULTI_ARCHITECTURE_RUN
