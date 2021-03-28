import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Handler
from ahriman.core.configuration import Configuration


def test_call(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must call inside lock
    """
    mocker.patch("ahriman.application.handlers.Handler.run")
    enter_mock = mocker.patch("ahriman.application.lock.Lock.__enter__")
    exit_mock = mocker.patch("ahriman.application.lock.Lock.__exit__")

    assert Handler._call(args, "x86_64", configuration)
    enter_mock.assert_called_once()
    exit_mock.assert_called_once()


def test_call_exception(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must process exception
    """
    mocker.patch("ahriman.application.lock.Lock.__enter__", side_effect=Exception())
    assert not Handler._call(args, "x86_64", configuration)
