#
# Copyright (c) 2021-2025 ahriman team.
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
from astroid import nodes
from collections.abc import Iterable
from enum import StrEnum
from pylint.checkers import BaseRawFileChecker
from pylint.lint import PyLinter
from typing import Any


class MethodType(StrEnum):
    """
    method type enumeration

    Attributes:
        Class(MethodType): (class attribute) class method
        Delete(MethodType): (class attribute) destructor-like methods
        Init(MethodType): (class attribute) initialization method
        Magic(MethodType): (class attribute) other magical methods
        New(MethodType): (class attribute) constructor method
        Normal(MethodType): (class attribute) usual method
        Property(MethodType): (class attribute) property method
        Static(MethodType): (class attribute) static method
    """

    Class = "classmethod"
    Delete = "del"
    Init = "init"
    Magic = "magic"
    New = "new"
    Normal = "regular"
    Property = "property"
    Static = "staticmethod"


class DefinitionOrder(BaseRawFileChecker):
    """
    check if methods are defined in recommended order

    Attributes:
        DECORATED_METHODS_ORDER(list[str]): (class attribute) predefined list of known function decorators
    """

    DECORATED_METHODS_ORDER = {
        "cached_property": MethodType.Property,
        "classmethod": MethodType.Class,
        "property": MethodType.Property,
        "staticmethod": MethodType.Static,
    }

    msgs = {
        "W6001": (
            "Invalid method order %s, expected %s",
            "methods-out-of-order",
            "Methods are defined out of recommended order.",
        ),
    }
    name = "method-ordering"
    options = (
        (
            "method-type-order",
            {
                "default": [
                    "init",
                    "new",
                    "del",
                    "property",
                    "classmethod",
                    "staticmethod",
                    "regular",
                    "magic",
                ],
                "type": "csv",
                "metavar": "<comma-separated types>",
                "help": "Method types order to check.",
            },
        ),
    )

    @staticmethod
    def methods(source: Iterable[Any], start_lineno: int = 0) -> list[nodes.FunctionDef]:
        """
        extract function nodes from list of raw nodes

        Args:
            source(Iterable[Any]): all available nodes
            start_lineno(int, optional): minimal allowed line number (Default value = 0)

        Returns:
            list[nodes.FunctionDef]: list of function nodes
        """
        def is_defined_function(function: Any) -> bool:
            return isinstance(function, nodes.FunctionDef) \
                and function.lineno is not None \
                and function.lineno >= start_lineno

        return list(filter(is_defined_function, source))

    @staticmethod
    def resolve_type(function: nodes.FunctionDef) -> MethodType:
        """
        resolve type of the function

        Args:
            function(nodes.FunctionDef): function definition

        Returns:
            MethodType: resolved function type
        """
        # init methods
        if function.name in ("__init__", "__post_init__"):
            return MethodType.Init
        if function.name in ("__new__",):
            return MethodType.New
        if function.name in ("__del__",):
            return MethodType.Delete

        # decorated methods
        decorators = []
        if function.decorators is not None:
            decorators = [getattr(decorator, "name", None) for decorator in function.decorators.get_children()]
        for decorator in decorators:
            if decorator in DefinitionOrder.DECORATED_METHODS_ORDER:
                return DefinitionOrder.DECORATED_METHODS_ORDER[decorator]

        # magic methods
        if function.name.startswith("__") and function.name.endswith("__"):
            return MethodType.Magic

        # normal method
        return MethodType.Normal

    def check_class(self, clazz: nodes.ClassDef) -> None:
        """
        check class functions ordering

        Args:
            clazz(nodes.ClassDef): class definition
        """
        methods = self.methods(clazz.values(), clazz.lineno)
        self.check_functions(methods)

    def check_functions(self, functions: list[nodes.FunctionDef]) -> None:
        """
        check global functions ordering

        Args:
            functions(list[nodes.FunctionDef]): list of functions in their defined order
        """
        for real, expected in zip(functions, sorted(functions, key=self.comparator)):
            if real == expected:
                continue
            self.add_message("methods-out-of-order", line=real.lineno, args=(real.name, expected.name))
            break

    def comparator(self, function: nodes.FunctionDef) -> tuple[int, str]:
        """
        compare key for sorting function

        Args:
            function(nodes.FunctionDef): function definition

        Returns:
            tuple[int, str]: comparison key for the specified function definition
        """
        function_type = self.resolve_type(function)
        try:
            function_type_index = self.linter.config.method_type_order.index(function_type)
        except ValueError:
            function_type_index = len(self.linter.config.method_type_order)  # not in the list

        return function_type_index, function.name

    def process_module(self, node: nodes.Module) -> None:
        """
        process module

        Args:
            node(nodes.Module): module node to check
        """
        # check global methods
        self.check_functions(self.methods(node.values()))
        # check class definitions
        for clazz in filter(lambda method: isinstance(method, nodes.ClassDef), node.values()):
            self.check_class(clazz)


def register(linter: PyLinter) -> None:
    """
    register custom checker

    Args:
        linter(PyLinter): linter in which checker should be registered
    """
    linter.register_checker(DefinitionOrder(linter))
