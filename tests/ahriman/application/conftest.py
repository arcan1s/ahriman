import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.application import Application
from ahriman.application.lock import Lock
from ahriman.core.configuration import Configuration


@pytest.fixture
def application(configuration: Configuration, mocker: MockerFixture) -> Application:
    mocker.patch("pathlib.Path.mkdir")
    return Application("x86_64", configuration)


@pytest.fixture
def args() -> argparse.Namespace:
    return argparse.Namespace(lock=None, force=False, unsafe=False, no_report=True)


@pytest.fixture
def lock(args: argparse.Namespace, configuration: Configuration) -> Lock:
    return Lock(args, "x86_64", configuration)
