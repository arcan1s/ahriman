import argparse

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.application.handlers import Restore
from ahriman.core.configuration import Configuration


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases
    :param args: command line arguments fixture
    :return: generated arguments for these test cases
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
    mocker.patch("tarfile.TarFile.__new__", return_value=tarfile)

    Restore.run(args, "x86_64", configuration, True, False)
    extract_mock.extractall.assert_called_once_with(path=args.output)


def test_disallow_auto_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Restore.ALLOW_AUTO_ARCHITECTURE_RUN
