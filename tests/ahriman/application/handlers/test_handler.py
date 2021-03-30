import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Handler


def test_call(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must call inside lock
    """
    args.configuration = ""
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
