import aiohttp_cors
import pytest

from aiohttp.web import Application


def test_setup_cors(application: Application) -> None:
    """
    must setup CORS
    """
    cors: aiohttp_cors.CorsConfig = application[aiohttp_cors.APP_CONFIG_KEY]
    # let's test here that it is enabled for all requests
    for route in application.router.routes():
        # we don't want to deal with match info here though
        try:
            url = route.url_for()
        except (KeyError, TypeError):
            continue
        request = pytest.helpers.request(application, url, route.method, resource=route.resource)
        assert cors._cors_impl._router_adapter.is_cors_enabled_on_request(request)
