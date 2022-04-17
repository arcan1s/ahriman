import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.handlers import Web
from ahriman.core.configuration import Configuration


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.parser = lambda: True
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.spawn.Spawn.start")
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    setup_mock = mocker.patch("ahriman.web.web.setup_service")
    run_mock = mocker.patch("ahriman.web.web.run_server")

    Web.run(args, "x86_64", configuration, True, False)
    setup_mock.assert_called_once_with("x86_64", configuration, pytest.helpers.anyvar(int))
    run_mock.assert_called_once_with(pytest.helpers.anyvar(int))


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
