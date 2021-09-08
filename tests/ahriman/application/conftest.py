import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.ahriman import _parser
from ahriman.application.application import Application
from ahriman.application.lock import Lock
from ahriman.core.configuration import Configuration


@pytest.fixture
def application(configuration: Configuration, mocker: MockerFixture) -> Application:
    """
    fixture for application
    :param configuration: configuration fixture
    :param mocker: mocker object
    :return: application test instance
    """
    mocker.patch("pathlib.Path.mkdir")
    return Application("x86_64", configuration, no_report=True)


@pytest.fixture
def args() -> argparse.Namespace:
    """
    fixture for command line arguments
    :return: command line arguments test instance
    """
    return argparse.Namespace(lock=None, force=False, unsafe=False, no_report=True)


@pytest.fixture
def lock(args: argparse.Namespace, configuration: Configuration) -> Lock:
    """
    fixture for file lock
    :param args: command line arguments fixture
    :param configuration: configuration fixture
    :return: file lock test instance
    """
    return Lock(args, "x86_64", configuration)


@pytest.fixture
def parser() -> argparse.ArgumentParser:
    """
    fixture for command line arguments parser
    :return: command line arguments parser test instance
    """
    return _parser()
