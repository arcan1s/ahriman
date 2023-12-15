from ahriman.core.configuration import Configuration
from ahriman.web.views.status_view_guard import StatusViewGuard


def test_routes(configuration: Configuration) -> None:
    """
    must correctly return routes list
    """
    StatusViewGuard.ROUTES = routes = ["route1", "route2"]
    assert StatusViewGuard.routes(configuration) == routes


def test_routes_empty(configuration: Configuration) -> None:
    """
    must return empty routes list if option is set
    """
    StatusViewGuard.ROUTES = ["route1", "route2"]
    configuration.set_option("web", "service_only", "yes")
    assert StatusViewGuard.routes(configuration) == []
