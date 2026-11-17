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
from astroid import nodes
from enum import StrEnum
from pylint.checkers import BaseChecker
from pylint.lint import PyLinter


class MethodType(StrEnum):
    """
    method type enumeration

    Attributes:
        CLASS_METHOD(MethodType): (class attribute) class method
        METHOD(MethodType): (class attribute) class method
    """
    CLASS_METHOD = "classmethod"
    METHOD = "method"


class TypeAnnotations(BaseChecker):
    """
    require explicit annotations on function parameters and return values
    """

    msgs = {
        "E5301": (
            "Missing type annotation for parameter %s",
            "missing-parameter-annotation",
            "Function parameters must have explicit type annotations, except method receivers.",
        ),
        "E5302": (
            "Missing return type annotation for function %s",
            "missing-return-annotation",
            "Functions must have explicit return annotations, including constructors and local functions.",
        ),
    }
    name = "type-annotations"

    def visit_asyncfunctiondef(self, node: nodes.AsyncFunctionDef) -> None:
        """
        check an asynchronous function signature

        Args:
            node(nodes.AsyncFunctionDef): function to check
        """
        self.visit_functiondef(node)

    def visit_functiondef(self, node: nodes.FunctionDef) -> None:
        """
        check a function signature

        Args:
            node(nodes.FunctionDef): function to check
        """
        args = node.args
        arguments = [*args.posonlyargs, *args.args, *args.kwonlyargs]
        annotations = [*args.posonlyargs_annotations, *args.annotations, *args.kwonlyargs_annotations]

        # remove receiver argument
        if arguments:
            match node.type:
                case MethodType.CLASS_METHOD | MethodType.METHOD:
                    arguments.pop(0)
                    annotations.pop(0)

        for argument, annotation in zip(arguments, annotations):
            if annotation is None:
                self.add_message("missing-parameter-annotation", node=argument, args=(argument.name,))

        for name, annotation in (
                (args.vararg, args.varargannotation),
                (args.kwarg, args.kwargannotation),
        ):
            if name is not None and annotation is None:
                self.add_message("missing-parameter-annotation", node=node, args=(name,))

        if node.returns is None:
            self.add_message("missing-return-annotation", node=node, args=(node.name,))


def register(linter: PyLinter) -> None:
    """
    register custom checker

    Args:
        linter(PyLinter): linter in which checker should be registered
    """
    linter.register_checker(TypeAnnotations(linter))
