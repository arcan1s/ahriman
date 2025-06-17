from aiohttp.web import Application
from pathlib import Path

from ahriman.core.configuration import Configuration
from ahriman.core.utils import walk
from ahriman.web.routes import _dynamic_routes, _identifier, setup_routes


def test_dynamic_routes(resource_path_root: Path, configuration: Configuration) -> None:
    """
    must return all available routes
    """
    views_root = resource_path_root / ".." / ".." / "src" / "ahriman" / "web" / "views"
    expected_views = [
        file
        for file in walk(views_root)
        if file.suffix == ".py" and file.name not in ("__init__.py", "base.py", "status_view_guard.py")
    ]

    routes = dict(_dynamic_routes(configuration))
    assert all(isinstance(view, type) for view in routes.values())
    assert len(set(routes.values())) == len(expected_views)


def test_identifier() -> None:
    """
    must correctly extract route identifiers
    """
    assert _identifier("/") == "_"
    assert _identifier("/api/v1/status") == "_api_v1_status"
    assert _identifier("/api/v1/packages/{package}") == "_api_v1_packages_:package"


def test_setup_routes(application: Application, configuration: Configuration) -> None:
    """
    must generate non-empty list of routes
    """
    application.router._named_resources = {}
    setup_routes(application, configuration)
    assert application.router.routes()
