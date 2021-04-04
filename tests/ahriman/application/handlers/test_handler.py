import argparse
import pytest

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.application.handlers import Handler
from ahriman.core.configuration import Configuration


def test_call(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must call inside lock
    """
    args.configuration = Path("")
    args.no_log = False
    mocker.patch("ahriman.application.handlers.Handler.run")
    mocker.patch("ahriman.core.configuration.Configuration.from_path")
    enter_mock = mocker.patch("ahriman.application.lock.Lock.__enter__")
    exit_mock = mocker.patch("ahriman.application.lock.Lock.__exit__")

    assert Handler._call(args, "x86_64")
    enter_mock.assert_called_once()
    exit_mock.assert_called_once()


def test_call_exception(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must process exception
    """
    mocker.patch("ahriman.application.lock.Lock.__enter__", side_effect=Exception())
    assert not Handler._call(args, "x86_64")


def test_execute(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must run execution in multiple processes
    """
    args.architecture = ["i686", "x86_64"]
    starmap_mock = mocker.patch("multiprocessing.pool.Pool.starmap")

    Handler.execute(args)
    starmap_mock.assert_called_once()


def test_packages(args: argparse.Namespace, configuration: Configuration) -> None:
    """
    must raise NotImplemented for missing method
    """
    with pytest.raises(NotImplementedError):
        Handler.run(args, "x86_64", configuration)
