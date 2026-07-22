import ahriman.web.views

from pathlib import Path

from ahriman.core.module_loader import _modules, implementations, optional_module
from ahriman.web.views.base import BaseView


def test_modules() -> None:
    """
    must load modules
    """
    modules = list(_modules(Path(next(iter(ahriman.web.views.__path__))), "ahriman.web.views"))
    assert modules
    assert all(not module.ispkg for module in modules)


def test_implementations() -> None:
    """
    must load implementations from the package
    """
    routes = list(implementations(ahriman.web.views, BaseView))
    assert routes
    assert all(isinstance(view, type) for view in routes)
    assert all(issubclass(view, BaseView) for view in routes)


def test_optional_module() -> None:
    """
    must import an available module
    """
    assert optional_module("ahriman.web.views") is ahriman.web.views


def test_optional_module_fallback() -> None:
    """
    must return none when the module cannot be imported
    """
    assert optional_module("missing_ahriman_module") is None
