import pytest

from aiohttp.web import Application
from importlib.machinery import ModuleSpec
from pathlib import Path
from pytest_mock import MockerFixture
from types import ModuleType

from ahriman.core.configuration import Configuration
from ahriman.core.util import walk
from ahriman.web.routes import _dynamic_routes, _module, _modules, setup_routes


def test_dynamic_routes(resource_path_root: Path) -> None:
    """
    must return all available routes
    """
    views_root = resource_path_root / ".." / ".." / "src" / "ahriman" / "web" / "views"
    expected_views = [
        file
        for file in walk(views_root)
        if file.suffix == ".py" and file.name not in ("__init__.py", "base.py")
    ]

    routes = _dynamic_routes(views_root)
    assert all(isinstance(view, type) for view in routes.values())
    assert len(set(routes.values())) == len(expected_views)


def test_module(mocker: MockerFixture) -> None:
    """
    must load module
    """
    exec_mock = mocker.patch("importlib.machinery.SourceFileLoader.exec_module")
    module_info = next(_modules(Path(__file__).parent))

    module = _module(module_info)
    assert isinstance(module, ModuleType)
    exec_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_module_no_spec(mocker: MockerFixture) -> None:
    """
    must raise ValueError if spec is not available
    """
    mocker.patch("importlib.machinery.FileFinder.find_spec", return_value=None)
    module_info = next(_modules(Path(__file__).parent))

    with pytest.raises(ValueError):
        _module(module_info)


def test_module_no_loader(mocker: MockerFixture) -> None:
    """
    must raise ValueError if loader is not available
    """
    mocker.patch("importlib.machinery.FileFinder.find_spec", return_value=ModuleSpec("name", None))
    module_info = next(_modules(Path(__file__).parent))

    with pytest.raises(ValueError):
        _module(module_info)


def test_modules() -> None:
    """
    must load modules
    """
    modules = list(_modules(Path(__file__).parent.parent))
    assert modules
    assert all(not module.ispkg for module in modules)


def test_setup_routes(application: Application, configuration: Configuration) -> None:
    """
    must generate non-empty list of routes
    """
    setup_routes(application, configuration.getpath("web", "static_path"))
    assert application.router.routes()
