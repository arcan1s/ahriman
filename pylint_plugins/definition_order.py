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
from astroid import nodes
from collections.abc import Iterable
from enum import Enum
from pylint.checkers import BaseRawFileChecker
from pylint.lint import PyLinter
from typing import Any


class MethodTypeOrder(int, Enum):
    """
    method type enumeration

    Attributes:
        New(MethodTypeOrder): (class attribute) constructor method
        Init(MethodTypeOrder): (class attribute) initialization method
        Property(MethodTypeOrder): (class attribute) property method
        Class(MethodTypeOrder): (class attribute) class method
        Static(MethodTypeOrder): (class attribute) static method
        Normal(MethodTypeOrder): (class attribute) usual method
        Magic(MethodTypeOrder): (class attribute) other magical methods
    """

    New = 0
    Init = 1
    Property = 2
    Class = 3
    Static = 4
    Normal = 5
    Magic = 6


class DefinitionOrder(BaseRawFileChecker):
    """
    check if methods are defined in recommended order

    Attributes:
        DECORATED_METHODS_ORDER(list[str]): (class attribute) predefined list of known function decorators
    """

    DECORATED_METHODS_ORDER = {
        "cached_property": MethodTypeOrder.Property,
        "classmethod": MethodTypeOrder.Class,
        "property": MethodTypeOrder.Property,
        "staticmethod": MethodTypeOrder.Static,
    }

    name = "method-ordering"
    msgs = {
        "W0001": (
            "Invalid method order %s, expected %s",
            "methods-out-of-order",
            "Methods are defined out of recommended order.",
        )
    }
    options = ()

    @staticmethod
    def comparator(function: nodes.FunctionDef) -> tuple[int, str]:
        """
        compare key for function node

        Args:
            function(nodes.FunctionDef): function definition

        Returns:
            tuple[int, str]: comparison key
        """
        # init methods
        if function.name in ("__new__",):
            return MethodTypeOrder.New, function.name
        if function.name in ("__init__", "__post_init__"):
            return MethodTypeOrder.Init, function.name

        # decorated methods
        decorators = []
        if function.decorators is not None:
            decorators = [getattr(decorator, "name", None) for decorator in function.decorators.get_children()]
        for decorator in decorators:
            if decorator in DefinitionOrder.DECORATED_METHODS_ORDER:
                return DefinitionOrder.DECORATED_METHODS_ORDER[decorator], function.name

        # magic methods
        if function.name.startswith("__") and function.name.endswith("__"):
            return MethodTypeOrder.Magic, function.name

        # normal method
        return MethodTypeOrder.Normal, function.name

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

    def check_class(self, clazz: nodes.ClassDef) -> None:
        """
        check class functions ordering

        Args:
            clazz(nodes.ClassDef): class definition
        """
        methods = DefinitionOrder.methods(clazz.values(), clazz.lineno)
        self.check_functions(methods)

    def check_functions(self, functions: list[nodes.FunctionDef]) -> None:
        """
        check global functions ordering

        Args:
            functions(list[nodes.FunctionDef]): list of functions in their defined order
        """
        for real, expected in zip(functions, sorted(functions, key=DefinitionOrder.comparator)):
            if real == expected:
                continue
            self.add_message("methods-out-of-order", line=real.lineno, args=(real.name, expected.name))
            break

    def process_module(self, node: nodes.Module) -> None:
        """
        process module

        Args:
            node(nodes.Module): module node to check
        """
        # check global methods
        self.check_functions(DefinitionOrder.methods(node.values()))
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
