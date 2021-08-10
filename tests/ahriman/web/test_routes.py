from aiohttp import web

from ahriman.web.routes import setup_routes


def test_setup_routes(application: web.Application) -> None:
    """
    must generate non empty list of routes
    """
    setup_routes(application)
    assert application.router.routes()
