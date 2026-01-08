#
# Copyright (c) 2021-2026 ahriman team.
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
import inspect

from collections.abc import Generator
from importlib import import_module
from pathlib import Path
from pkgutil import ModuleInfo, walk_packages
from types import ModuleType
from typing import Any, TypeGuard, TypeVar


__all__ = ["implementations"]


T = TypeVar("T")


def _modules(module_root: Path, prefix: str) -> Generator[ModuleInfo, None, None]:
    """
    extract available modules from package

    Args:
        module_root(Path): module root path
        prefix(str): modules package prefix

    Yields:
        ModuleInfo: module information each available module
    """
    prefix = f"{prefix}." if prefix else ""
    for module_info in walk_packages([str(module_root)], prefix):
        if module_info.ispkg:
            yield from _modules(module_root / module_info.name, prefix)
        else:
            yield module_info


def implementations(root_module: ModuleType, base_class: type[T]) -> Generator[type[T], None, None]:
    """
    extract implementations of the ``base_class`` from the module

    Args:
        root_module(ModuleType): root module
        base_class(type[T]): base class type

    Yields:
        type[T]: found implementations
    """
    def is_base_class(clazz: Any) -> TypeGuard[type[T]]:
        return inspect.isclass(clazz) \
            and issubclass(clazz, base_class) and clazz != base_class \
            and clazz.__module__ == module.__name__

    prefix = root_module.__name__

    for module_root in root_module.__path__:
        for module_info in _modules(Path(module_root), prefix):
            module = import_module(module_info.name)

            for _, attribute in inspect.getmembers(module, is_base_class):
                yield attribute
