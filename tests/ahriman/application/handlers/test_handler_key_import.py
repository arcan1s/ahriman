import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import KeyImport
from ahriman.core.configuration import Configuration


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.key = "0xE989490C"
    args.key_server = "keyserver.ubuntu.com"
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.core.sign.gpg.GPG.key_import")

    KeyImport.run(args, "x86_64", configuration, report=False, unsafe=False)
    application_mock.assert_called_once_with(args.key_server, args.key)


def test_disallow_auto_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not KeyImport.ALLOW_AUTO_ARCHITECTURE_RUN
