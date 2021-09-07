import pytest

from aiohttp import web
from collections import namedtuple
from pytest_mock import MockerFixture
from typing import Any

import ahriman.core.auth.helpers

from ahriman.core.configuration import Configuration
from ahriman.core.spawn import Spawn
from ahriman.models.user import User
from ahriman.web.web import setup_service


_request = namedtuple("_request", ["app", "path", "method", "json", "post"])


@pytest.helpers.register
def request(app: web.Application, path: str, method: str, json: Any = None, data: Any = None) -> _request:
    """
    request generator helper
    :param app: application fixture
    :param path: path for the request
    :param method: method for the request
    :param json: json payload of the request
    :param data: form data payload of the request
    :return: dummy request object
    """
    return _request(app, path, method, json, data)


@pytest.fixture
def application(configuration: Configuration, spawner: Spawn, mocker: MockerFixture) -> web.Application:
    """
    application fixture
    :param configuration: configuration fixture
    :param spawner: spawner fixture
    :param mocker: mocker object
    :return: application test instance
    """
    mocker.patch.object(ahriman.core.auth.helpers, "_has_aiohttp_security", False)
    mocker.patch("pathlib.Path.mkdir")
    return setup_service("x86_64", configuration, spawner)


@pytest.fixture
def application_with_auth(configuration: Configuration, user: User, spawner: Spawn,
                          mocker: MockerFixture) -> web.Application:
    """
    application fixture with auth enabled
    :param configuration: configuration fixture
    :param user: user descriptor fixture
    :param spawner: spawner fixture
    :param mocker: mocker object
    :return: application test instance
    """
    configuration.set_option("auth", "target", "configuration")
    mocker.patch.object(ahriman.core.auth.helpers, "_has_aiohttp_security", True)
    mocker.patch("pathlib.Path.mkdir")
    application = setup_service("x86_64", configuration, spawner)

    generated = User(user.username, user.hash_password(application["validator"].salt), user.access)
    application["validator"]._users[generated.username] = generated

    return application
