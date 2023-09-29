#
# Copyright (c) 2021-2023 ahriman team.
#
# This file is part of ahriman
# (see https://github.com/arcan1s/ahriman).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from aiohttp.web import Application, View
from collections.abc import Generator
from importlib.machinery import SourceFileLoader
from pathlib import Path
from pkgutil import ModuleInfo, iter_modules
from types import ModuleType
from typing import Any, Type, TypeGuard

from ahriman.web.views.base import BaseView


__all__ = ["setup_routes"]


def _dynamic_routes(module_root: Path) -> dict[str, Type[View]]:
    """
    extract dynamic routes based on views

    Args:
        module_root(Path): root module path with views

    Returns:
        dict[str, Type[View]]: map of the route to its view
    """
    def is_base_view(clz: Any) -> TypeGuard[Type[BaseView]]:
        return isinstance(clz, type) and issubclass(clz, BaseView)

    routes: dict[str, Type[View]] = {}
    for module_info in _modules(module_root):
        module = _module(module_info)

        for attribute_name in dir(module):
            view = getattr(module, attribute_name)
            if not is_base_view(view):
                continue
            routes.update([(route, view) for route in view.ROUTES])

    return routes


def _module(module_info: ModuleInfo) -> ModuleType:
    """
    load module from its info

    Args:
        module_info(ModuleInfo): module info descriptor

    Returns:
        ModuleType: loaded module

    Raises:
        ValueError: if loader is not an instance of ``SourceFileLoader``
    """
    module_spec = module_info.module_finder.find_spec(module_info.name, None)
    if module_spec is None:
        raise ValueError(f"Module specification of {module_info.name} is empty")

    loader = module_spec.loader
    if not isinstance(loader, SourceFileLoader):
        raise ValueError(f"Module {module_info.name} loader is not an instance of SourceFileLoader")

    module = ModuleType(loader.name)
    loader.exec_module(module)

    return module


def _modules(module_root: Path) -> Generator[ModuleInfo, None, None]:
    """
    extract available modules from package

    Args:
        module_root(Path): module root path

    Yields:
        ModuleInfo: module information each available module
    """
    for module_info in iter_modules([str(module_root)]):
        if module_info.ispkg:
            yield from _modules(module_root / module_info.name)
        else:
            yield module_info


def setup_routes(application: Application, static_path: Path) -> None:
    """
    setup all defined routes

    Args:
        application(Application): web application instance
        static_path(Path): path to static files directory
    """
    application.router.add_static("/static", static_path, follow_symlinks=True)

    views = Path(__file__).parent / "views"
    for route, view in _dynamic_routes(views).items():
        application.router.add_view(route, view)
