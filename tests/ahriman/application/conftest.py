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
def lock(configuration: Configuration) -> Lock:
    return Lock(argparse.Namespace(lock=None, force=False, unsafe=False, no_report=True),
                "x86_64", configuration)
