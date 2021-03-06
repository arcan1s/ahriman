import pytest

from aiohttp import web
from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.web.web import setup_service


@pytest.fixture
def application(configuration: Configuration, mocker: MockerFixture) -> web.Application:
    mocker.patch("pathlib.Path.mkdir")
    return setup_service("x86_64", configuration)
