import pytest

from aiohttp import web
from pytest_mock import MockerFixture

import ahriman.core.auth.helpers

from ahriman.core.configuration import Configuration
from ahriman.models.user import User
from ahriman.web.web import setup_service


@pytest.fixture
def application(configuration: Configuration, mocker: MockerFixture) -> web.Application:
    """
    application fixture
    :param configuration: configuration fixture
    :param mocker: mocker object
    :return: application test instance
    """
    mocker.patch.object(ahriman.core.auth.helpers, "_has_aiohttp_security", False)
    mocker.patch("pathlib.Path.mkdir")
    return setup_service("x86_64", configuration)


@pytest.fixture
def application_with_auth(configuration: Configuration, user: User, mocker: MockerFixture) -> web.Application:
    """
    application fixture with auth enabled
    :param configuration: configuration fixture
    :param user: user descriptor fixture
    :param mocker: mocker object
    :return: application test instance
    """
    configuration.set("web", "auth", "yes")
    mocker.patch.object(ahriman.core.auth.helpers, "_has_aiohttp_security", True)
    mocker.patch("pathlib.Path.mkdir")
    application = setup_service("x86_64", configuration)

    generated = User(user.username, user.generate_password(user.password, application["validator"].salt), user.access)
    application["validator"].users[generated.username] = generated

    return application
