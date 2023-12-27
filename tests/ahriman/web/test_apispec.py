import pytest

from aiohttp.web import Application
from pytest_mock import MockerFixture

from ahriman import __version__
from ahriman.web.apispec import _info, _security, _servers, setup_apispec
from ahriman.web.keys import ConfigurationKey


def test_info() -> None:
    """
    must generate info object for swagger
    """
    info = _info()
    assert info["title"] == "ahriman"
    assert info["version"] == __version__


def test_security() -> None:
    """
    must generate security definitions for swagger
    """
    token = next(iter(_security()))["token"]
    assert token == {"type": "apiKey", "name": "API_SESSION", "in": "cookie"}


def test_servers(application: Application) -> None:
    """
    must generate servers definitions
    """
    servers = _servers(application)
    assert servers == [{"url": "http://127.0.0.1:8080"}]


def test_servers_address(application: Application) -> None:
    """
    must generate servers definitions with address
    """
    application[ConfigurationKey].set_option("web", "address", "https://example.com")
    servers = _servers(application)
    assert servers == [{"url": "https://example.com"}]


def test_setup_apispec(application: Application, mocker: MockerFixture) -> None:
    """
    must set api specification
    """
    apispec_mock = mocker.patch("aiohttp_apispec.setup_aiohttp_apispec")
    setup_apispec(application)
    apispec_mock.assert_called_once_with(
        application,
        url="/api-docs/swagger.json",
        openapi_version="3.0.2",
        info=pytest.helpers.anyvar(int),
        servers=pytest.helpers.anyvar(int),
        security=pytest.helpers.anyvar(int),
    )
