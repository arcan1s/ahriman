import pytest

from aiohttp import web
from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.web.web import setup_service


@pytest.fixture
def application(configuration: Configuration, mocker: MockerFixture) -> web.Application:
    """
    application fixture
    :param configuration: configuration fixture
    :param mocker: mocker object
    :return: application test instance
    """
    mocker.patch("pathlib.Path.mkdir")
    return setup_service("x86_64", configuration)


@pytest.fixture
def application_with_auth(configuration: Configuration, mocker: MockerFixture) -> web.Application:
    """
    application fixture with auth enabled
    :param configuration: configuration fixture
    :param mocker: mocker object
    :return: application test instance
    """
    configuration.set("web", "auth", "yes")
    mocker.patch("pathlib.Path.mkdir")
    return setup_service("x86_64", configuration)
