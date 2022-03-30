import pytest

from aiohttp import web
from collections import namedtuple
from pytest_mock import MockerFixture
from typing import Any

import ahriman.core.auth.helpers

from ahriman.core.configuration import Configuration
from ahriman.core.database.sqlite import SQLite
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
def application(configuration: Configuration, spawner: Spawn, database: SQLite,
                mocker: MockerFixture) -> web.Application:
    """
    application fixture
    :param configuration: configuration fixture
    :param spawner: spawner fixture
    :param database: database fixture
    :param mocker: mocker object
    :return: application test instance
    """
    mocker.patch("ahriman.core.database.sqlite.SQLite.load", return_value=database)
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch.object(ahriman.core.auth.helpers, "_has_aiohttp_security", False)
    return setup_service("x86_64", configuration, spawner)


@pytest.fixture
def application_with_auth(configuration: Configuration, user: User, spawner: Spawn, database: SQLite,
                          mocker: MockerFixture) -> web.Application:
    """
    application fixture with auth enabled
    :param configuration: configuration fixture
    :param user: user descriptor fixture
    :param spawner: spawner fixture
    :param database: database fixture
    :param mocker: mocker object
    :return: application test instance
    """
    configuration.set_option("auth", "target", "configuration")
    mocker.patch("ahriman.core.database.sqlite.SQLite.load", return_value=database)
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch.object(ahriman.core.auth.helpers, "_has_aiohttp_security", True)
    application = setup_service("x86_64", configuration, spawner)

    generated = user.hash_password(application["validator"].salt)
    mocker.patch("ahriman.core.database.sqlite.SQLite.user_get", return_value=generated)

    return application


@pytest.fixture
def application_with_debug(configuration: Configuration, user: User, spawner: Spawn, database: SQLite,
                           mocker: MockerFixture) -> web.Application:
    """
    application fixture with debug enabled
    :param configuration: configuration fixture
    :param user: user descriptor fixture
    :param spawner: spawner fixture
    :param database: database fixture
    :param mocker: mocker object
    :return: application test instance
    """
    configuration.set_option("web", "debug", "yes")
    mocker.patch("ahriman.core.database.sqlite.SQLite.load", return_value=database)
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch.object(ahriman.core.auth.helpers, "_has_aiohttp_security", False)
    return setup_service("x86_64", configuration, spawner)
