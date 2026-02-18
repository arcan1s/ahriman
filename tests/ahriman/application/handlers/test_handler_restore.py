import argparse

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.application.handlers.restore import Restore
from ahriman.core.configuration import Configuration


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.path = Path("result.tar.gz")
    args.output = Path.cwd()
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    tarfile = MagicMock()
    extract_mock = tarfile.__enter__.return_value = MagicMock()
    mocker.patch("ahriman.application.handlers.restore.tarfile.open", return_value=tarfile)

    _, repository_id = configuration.check_loaded()
    Restore.run(args, repository_id, configuration, report=False)
    extract_mock.extractall.assert_called_once_with(path=args.output, filter="data")


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Restore.ALLOW_MULTI_ARCHITECTURE_RUN
