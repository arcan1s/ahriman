import pytest
import pytest_asyncio

from aiohttp.test_utils import TestClient
from aiohttp.web import Application, Resource, UrlMappingMatchInfo
from collections.abc import Awaitable, Callable
from marshmallow import Schema
from pytest_mock import MockerFixture
from typing import Any
from unittest.mock import MagicMock, Mock

from ahriman.core.auth import helpers
from ahriman.core.auth.oauth import OAuth
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.spawn import Spawn
from ahriman.models.user import User
from ahriman.web.keys import AuthKey
from ahriman.web.web import setup_server


@pytest.helpers.register
def patch_view(application: Application, attribute: str, mock: Mock) -> Mock:
    """
    patch given attribute in views. This method is required because of dynamic load

    Args:
        application(Application): application fixture
        attribute(str): attribute name to patch
        mock(Mock): mock object

    Returns:
        Mock: mock set to object
    """
    for route in application.router.routes():
        if hasattr(route.handler, attribute):
            setattr(route.handler, attribute, mock)

    return mock


@pytest.helpers.register
def request(application: Application, path: str, method: str, params: Any = None, json: Any = None, data: Any = None,
            extra: dict[str, Any] | None = None, resource: Resource | None = None) -> MagicMock:
    """
    request generator helper

    Args:
        application(Application): application fixture
        path(str): path for the request
        method(str): method for the request
        params(Any, optional): query parameters (Default value = None)
        json(Any, optional): json payload of the request (Default value = None)
        data(Any, optional): form data payload of the request (Default value = None)
        extra(dict[str, Any] | None, optional): extra info which will be injected for ``get_extra_info`` command
        resource(Resource | None, optional): optional web resource for the request (Default value = None)

    Returns:
        MagicMock: dummy request mock
    """
    request_mock = MagicMock()
    request_mock.app = application
    request_mock.path = path
    request_mock.method = method
    request_mock.query = params
    request_mock.json = json
    request_mock.post = data

    if resource is not None:
        route_mock = MagicMock()
        route_mock.resource = resource
        request_mock.match_info = UrlMappingMatchInfo({}, route_mock)

    extra = extra or {}
    request_mock.get_extra_info.side_effect = extra.get

    return request_mock


@pytest.helpers.register
def schema_request(handler: Callable[..., Awaitable[Any]], *, location: str = "json") -> Schema:
    """
    extract request schema from docs

    Args:
        handler(Callable[[], Awaitable[Any]]): request handler
        location(str, optional): location of the request (Default value = "json")

    Returns:
        Schema: request schema as set by the decorators
    """
    schemas: list[dict[str, Any]] = handler.__schemas__  # type: ignore[attr-defined]
    return next(schema["schema"] for schema in schemas if schema["put_into"] == location)


@pytest.helpers.register
def schema_response(handler: Callable[..., Awaitable[Any]], *, code: int = 200) -> Schema:
    """
    extract response schema from docs

    Args:
        handler(Callable[[], Awaitable[Any]]): request handler
        code(int, optional): return code of the request (Default value = 200)

    Returns:
        Schema: response schema as set by the decorators
    """
    schemas: dict[int, Any] = handler.__apispec__["responses"]  # type: ignore[attr-defined]
    schema = schemas[code]["schema"]
    if callable(schema):
        schema = schema()
    return schema


@pytest.fixture
def application(configuration: Configuration, spawner: Spawn, database: SQLite, mocker: MockerFixture) -> Application:
    """
    application fixture

    Args:
        configuration(Configuration): configuration fixture
        spawner(Spawn): spawner fixture
        database(SQLite): database fixture
        mocker(MockerFixture): mocker object

    Returns:
        Application: application test instance
    """
    configuration.set_option("web", "port", "8080")
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    mocker.patch("aiohttp_apispec.setup_aiohttp_apispec")
    mocker.patch.object(helpers, "aiohttp_security", None)
    _, repository_id = configuration.check_loaded()

    return setup_server(configuration, spawner, [repository_id])


@pytest.fixture
def application_with_auth(configuration: Configuration, user: User, spawner: Spawn, database: SQLite,
                          mocker: MockerFixture) -> Application:
    """
    application fixture with auth enabled

    Args:
        configuration(Configuration): configuration fixture
        user(User): user descriptor fixture
        spawner(Spawn): spawner fixture
        database(SQLite): database fixture
        mocker(MockerFixture): mocker object

    Returns:
        Application: application test instance
    """
    configuration.set_option("auth", "target", "configuration")
    configuration.set_option("web", "port", "8080")
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    mocker.patch("aiohttp_apispec.setup_aiohttp_apispec")
    _, repository_id = configuration.check_loaded()
    application = setup_server(configuration, spawner, [repository_id])

    generated = user.hash_password(application[AuthKey].salt)
    mocker.patch("ahriman.core.database.SQLite.user_get", return_value=generated)

    return application


@pytest_asyncio.fixture
async def client(application: Application, aiohttp_client: Any, mocker: MockerFixture) -> TestClient:
    """
    web client fixture

    Args:
        application(Application): application fixture
        aiohttp_client(Any): aiohttp client fixture
        mocker(MockerFixture): mocker object

    Returns:
        TestClient: web client test instance
    """
    mocker.patch("pathlib.Path.iterdir", return_value=[])
    return await aiohttp_client(application)


@pytest_asyncio.fixture
async def client_with_auth(application_with_auth: Application, aiohttp_client: Any,
                           mocker: MockerFixture) -> TestClient:
    """
    web client fixture with full authorization functions

    Args:
        application_with_auth(Application): application fixture
        aiohttp_client(Any): aiohttp client fixture
        mocker(MockerFixture): mocker object

    Returns:
        TestClient: web client test instance
    """
    mocker.patch("pathlib.Path.iterdir", return_value=[])
    return await aiohttp_client(application_with_auth)


@pytest_asyncio.fixture
async def client_with_oauth_auth(application_with_auth: Application, aiohttp_client: Any,
                                 mocker: MockerFixture) -> TestClient:
    """
    web client fixture with full authorization functions

    Args:
        application_with_auth(Application): application fixture
        aiohttp_client(Any): aiohttp client fixture
        mocker(MockerFixture): mocker object

    Returns:
        TestClient: web client test instance
    """
    mocker.patch("pathlib.Path.iterdir", return_value=[])
    application_with_auth[AuthKey] = MagicMock(spec=OAuth)
    return await aiohttp_client(application_with_auth)
