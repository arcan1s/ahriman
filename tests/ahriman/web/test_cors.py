import aiohttp_cors
import pytest

from aiohttp.web import Application
from pytest_mock import MockerFixture

from ahriman.web.cors import setup_cors
from ahriman.web.keys import ConfigurationKey


def test_setup_cors(application: Application) -> None:
    """
    must setup CORS
    """
    cors = application[aiohttp_cors.APP_CONFIG_KEY]
    # let's test here that it is enabled for all requests
    for route in application.router.routes():
        # we don't want to deal with match info here though
        try:
            url = route.url_for()
        except (KeyError, TypeError):
            continue
        request = pytest.helpers.request(application, url, route.method, resource=route.resource)
        assert cors._cors_impl._router_adapter.is_cors_enabled_on_request(request)


def test_setup_cors_custom_origins(application: Application, mocker: MockerFixture) -> None:
    """
    must setup CORS with custom origins
    """
    configuration = application[ConfigurationKey]
    configuration.set_option("web", "cors_allow_origins", "https://example.com https://httpbin.com")

    setup_mock = mocker.patch("ahriman.web.cors.aiohttp_cors.setup", return_value=mocker.MagicMock())
    setup_cors(application, configuration)

    defaults = setup_mock.call_args.kwargs["defaults"]
    assert "https://example.com" in defaults
    assert "https://httpbin.com" in defaults
    assert "*" not in defaults


def test_setup_cors_custom_methods(application: Application, mocker: MockerFixture) -> None:
    """
    must setup CORS with custom methods
    """
    configuration = application[ConfigurationKey]
    configuration.set_option("web", "cors_allow_methods", "GET POST")

    setup_mock = mocker.patch("ahriman.web.cors.aiohttp_cors.setup", return_value=mocker.MagicMock())
    setup_cors(application, configuration)

    defaults = setup_mock.call_args.kwargs["defaults"]
    resource_options = next(iter(defaults.values()))
    assert resource_options.allow_methods == {"GET", "POST"}
