import ahriman.web.views

from pathlib import Path

from ahriman.core.module_loader import _modules, implementations
from ahriman.web.views.base import BaseView


def test_implementations() -> None:
    """
    must load implementations from the package
    """
    routes = list(implementations(ahriman.web.views, BaseView))
    assert routes
    assert all(isinstance(view, type) for view in routes)
    assert all(issubclass(view, BaseView) for view in routes)


def test_modules() -> None:
    """
    must load modules
    """
    modules = list(_modules(Path(__file__).parent.parent, "ahriman.web.views"))
    assert modules
    assert all(not module.ispkg for module in modules)
