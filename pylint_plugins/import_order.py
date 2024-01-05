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
from enum import StrEnum
from pylint.checkers import BaseRawFileChecker
from pylint.lint import PyLinter
from typing import Any


class ImportType(StrEnum):
    """
    import type enumeration

    Attributes:
        Package(MethodTypeOrder): (class attribute) package import
        PackageFrom(MethodTypeOrder): (class attribute) package import, from clause
        System(ImportType): (class attribute) system installed packages
        SystemFrom(MethodTypeOrder): (class attribute) system installed packages, from clause
    """

    Package = "package"
    PackageFrom = "package-from"
    System = "system"
    SystemFrom = "system-from"


class ImportOrder(BaseRawFileChecker):
    """
    check if imports are defined in recommended order
    """

    msgs = {
        "W6002": (
            "Invalid import order %s, expected before %s",
            "imports-out-of-order",
            "Imports are defined out of recommended order.",
        ),
        "W6003": (
            "Import contains more than one package: %s",
            "multiple-package-imports",
            "Multiple package imports are not allowed.",
        ),
        "W6004": (
            "Invalid from import order %s, expected %s",
            "from-imports-out-of-order",
            "From imports are defined out of recommended order.",
        ),
    }
    name = "import-ordering"
    options = (
        (
            "import-type-order",
            {
                "default": [
                    "system",
                    "system-from",
                    "package",
                    "package-from",
                ],
                "type": "csv",
                "metavar": "<comma-separated types>",
                "help": "Import types order to check.",
            },
        ),
        (
            "root-module",
            {
                "default": "ahriman",
                "type": "string",
                "help": "Root module name",
            }
        )
    )

    @staticmethod
    def imports(source: Iterable[Any], start_lineno: int = 0) -> list[nodes.Import | nodes.ImportFrom]:
        """
        extract import nodes from list of raw nodes

        Args:
            source(Iterable[Any]): all available nodes
            start_lineno(int, optional): minimal allowed line number (Default value = 0)

        Returns:
            list[nodes.Import | nodes.ImportFrom]: list of import nodes
        """

        def is_defined_import(imports: Any) -> bool:
            return isinstance(imports, (nodes.Import, nodes.ImportFrom)) \
                and imports.lineno is not None \
                and imports.lineno >= start_lineno

        return list(filter(is_defined_import, source))

    def check_from_imports(self, imports: nodes.ImportFrom) -> None:
        """
        check import from statement

        Args:
            imports(nodes.ImportFrom): import from node
        """
        imported = [names for names, _ in imports.names]
        for real, expected in zip(imported, sorted(imported)):
            if real == expected:
                continue
            self.add_message("from-imports-out-of-order", line=imports.lineno, args=(real, expected))
            break

    def check_imports(self, imports: list[nodes.Import | nodes.ImportFrom], root_package: str) -> None:
        """
        check imports

        Args:
            imports(list[nodes.Import | nodes.ImportFrom]): list of imports in their defined order
            root_package(str): root package name
        """
        last_statement: tuple[int, str] | None = None

        for statement in imports:
            # define types and perform specific checks
            if isinstance(statement, nodes.ImportFrom):
                import_name = statement.modname
                root, *_ = import_name.split(".", maxsplit=1)
                import_type = ImportType.PackageFrom if root_package == root else ImportType.SystemFrom
                # check from import itself
                self.check_from_imports(statement)
            else:
                import_name = next(name for name, _ in statement.names)
                root, *_ = import_name.split(".", maxsplit=1)[0]
                import_type = ImportType.Package if root_package == root else ImportType.System
                # check import itself
                self.check_package_imports(statement)

            # extract index
            try:
                import_type_index = self.linter.config.import_type_order.index(import_type)
            except ValueError:
                import_type_index = len(self.linter.config.import_type_order)

            # check ordering if possible
            if last_statement is not None:
                _, last_statement_name = last_statement
                if last_statement > (import_type_index, import_name):
                    self.add_message("imports-out-of-order", line=statement.lineno,
                                     args=(import_name, last_statement_name))

            # update the last value
            last_statement = import_type_index, import_name

    def check_package_imports(self, imports: nodes.Import) -> None:
        """
        check package import

        Args:
            imports(nodes.Import): package import node
        """
        if len(imports.names) != 1:
            self.add_message("multiple-package-imports", line=imports.lineno, args=(imports.names,))

    def process_module(self, node: nodes.Module) -> None:
        """
        process module

        Args:
            node(nodes.Module): module node to check
        """
        root_module, *_ = node.qname().split(".")
        self.check_imports(self.imports(node.values()), root_module)


def register(linter: PyLinter) -> None:
    """
    register custom checker

    Args:
        linter(PyLinter): linter in which checker should be registered
    """
    linter.register_checker(ImportOrder(linter))
