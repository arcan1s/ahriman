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
import re
import shlex
import tree_sitter_bash

from collections.abc import Iterable, Iterator
from enum import StrEnum
from tree_sitter import Language, Node, Parser
from typing import IO, cast

from ahriman.core.exceptions import PkgbuildParserError
from ahriman.models.pkgbuild_patch import PkgbuildPatch


class PkgbuildNodeType(StrEnum):
    """
    tree-sitter node types used by parser

    Attributes:
        Append(PkgbuildNodeType): append node
        Array(PkgbuildNodeType): array node
        Comment(PkgbuildNodeType): comment node
        Concatenation(PkgbuildNodeType): concatenation node
        Error(PkgbuildNodeType): syntax error node
        FunctionDefinition(PkgbuildNodeType): function definition node
        Number(PkgbuildNodeType): numeric word node
        RawString(PkgbuildNodeType): single-quoted string node
        String(PkgbuildNodeType): double-quoted string node
        StringContent(PkgbuildNodeType): string content node
        VariableAssignment(PkgbuildNodeType): assignment node
        Word(PkgbuildNodeType): word node
    """

    Append = "+="
    Array = "array"
    Comment = "comment"
    Concatenation = "concatenation"
    Error = "ERROR"
    FunctionDefinition = "function_definition"
    Number = "number"
    RawString = "raw_string"
    String = "string"
    StringContent = "string_content"
    VariableAssignment = "variable_assignment"
    Word = "word"


class PkgbuildNodeField(StrEnum):
    """
    tree-sitter node fields used by parser

    Attributes:
        Body(PkgbuildNodeField): function body field
        Name(PkgbuildNodeField): variable or function name field
        Value(PkgbuildNodeField): assignment value field
    """

    Body = "body"
    Name = "name"
    Value = "value"


class PkgbuildParser(Iterable[PkgbuildPatch]):
    """
    PKGBUILD parser implementation in python

    What it is:

    #. A PKGBUILD parser based on tree-sitter's bash grammar.
    #. A parser for assignments, arrays, and functions.
    #. A parser which does not execute shell code.

    What it is not:

    #. A shell executor.
    #. A shell interpreter. Variable and command substitutions are returned as written.

    Simple comma-separated brace expressions in array elements are expanded. Function bodies are returned from the
    original source, with their formatting preserved. Assignments inside shell statements and control-flow nodes are
    extracted without checking whether those statements would run.

    Each iteration parses the stored source independently, starting from the beginning.

    Examples:
        Parse package assignments::

            >>> source = b"pkgname=example\\npkgver=1\\n"
            >>> for patch in PkgbuildParser(BytesIO(source)):
            ...     print(patch.key, patch.value)

        Function bodies are returned as function patches::

            >>> source = b"pkgver() { printf 1; }"
            >>> for patch in PkgbuildParser(BytesIO(source)):
            ...     print(patch.key, patch.value)
    """

    _BRACE_EXPANSION = re.compile(r"(.*)\{([^{}]+)\}(.*)")

    def __init__(self, stream: IO[bytes]) -> None:
        """
        Args:
            stream(IO[bytes]): input PKGBUILD stream
        """
        self._content = stream.read()

    @staticmethod
    def _expand_array(value: str, *, expand: bool = True) -> list[str]:
        """
        expand comma-separated brace expressions in a value

        Args:
            value(str): value that may contain a brace expression
            expand(bool, optional): whether brace expansion is allowed (Default value = True)

        Returns:
            list[str]: expanded values if applicable
        """
        match = PkgbuildParser._BRACE_EXPANSION.fullmatch(value)
        # if there is no comma inside it should be treated as normal value
        if match is None or not expand or "," not in match.group(2):
            return [value]

        prefix, values, suffix = match.groups()
        return [f"{prefix}{item}{suffix}" for item in values.split(",")]

    @staticmethod
    def _text(node: Node) -> str:
        """
        read the original source text represented by a syntax tree node

        Args:
            node(Node): syntax tree node to read

        Returns:
            str: source text for the node
        """
        return cast(bytes, node.text).decode("utf8", errors="backslashreplace")

    def _assignment(self, node: Node) -> PkgbuildPatch:
        """
        convert an assignment node

        Args:
            node(Node): assignment node to convert

        Returns:
            PkgbuildPatch: parsed assignment
        """
        name = cast(Node, node.child_by_field_name(PkgbuildNodeField.Name))
        value = cast(Node, node.child_by_field_name(PkgbuildNodeField.Value))
        key = self._text(name)

        match value.type:
            case PkgbuildNodeType.Array:
                array_values = []
                for element in filter(lambda child: child.type != PkgbuildNodeType.Comment, value.named_children):
                    item = self._value(element)
                    values = self._expand_array(item, expand=element.type == PkgbuildNodeType.Concatenation)
                    array_values.extend(values)
                return PkgbuildPatch(key, array_values)

            case _:
                return PkgbuildPatch(key, self._value(value))

    def _read(self, node: Node) -> Iterator[PkgbuildPatch]:
        """
        find assignments and functions in a syntax tree node

        Args:
            node(Node): syntax tree node to inspect

        Yields:
            PkgbuildPatch: parsed entries
        """
        match node.type:
            case PkgbuildNodeType.VariableAssignment if not any(child.type == PkgbuildNodeType.Append for child in node.children):
                yield self._assignment(node)

            case PkgbuildNodeType.FunctionDefinition:
                name = cast(Node, node.child_by_field_name(PkgbuildNodeField.Name))
                body = cast(Node, node.child_by_field_name(PkgbuildNodeField.Body))
                yield PkgbuildPatch(f"{self._text(name)}()", self._text(body))

            case _:
                # descend into statements, but skip command arguments and values
                for child in node.named_children:
                    if child.type not in (
                            PkgbuildNodeType.Array,
                            PkgbuildNodeType.Comment,
                            PkgbuildNodeType.RawString,
                            PkgbuildNodeType.String,
                            PkgbuildNodeType.Word,
                    ):
                        yield from self._read(child)

    def _value(self, node: Node) -> str:
        """
        extract a string value from a syntax tree node

        Args:
            node(Node): syntax tree node to extract

        Returns:
            str: extracted string value
        """
        if node.type in (PkgbuildNodeType.Concatenation, PkgbuildNodeType.String):
            return "".join(self._value(child) for child in node.named_children)

        value = self._text(node)
        match node.type:
            case PkgbuildNodeType.StringContent:
                value = f'"{value}"'
            case PkgbuildNodeType.Number | PkgbuildNodeType.RawString | PkgbuildNodeType.Word:
                pass
            case _:
                return value

        return "".join(shlex.split(value, comments=False, posix=True))

    def parse(self) -> Iterator[PkgbuildPatch]:
        """
        parse source and yield extracted entries

        Yields:
            PkgbuildPatch: parsed entries

        Raises:
            PkgbuildParserError: source contains invalid shell syntax
        """
        def walk(node: Node) -> Iterator[Node]:
            yield node
            for child in node.children:
                yield from walk(child)

        parser = Parser(Language(tree_sitter_bash.language()))
        tree = parser.parse(self._content)

        if tree.root_node.has_error:
            error = next((node for node in walk(tree.root_node) if node.is_error or node.is_missing), tree.root_node)
            raise PkgbuildParserError(
                f"syntax error at line {error.start_point.row + 1}, column {error.start_point.column + 1}"
            )

        yield from self._read(tree.root_node)

    def __iter__(self) -> Iterator[PkgbuildPatch]:
        """
        iterate over the parsed entries

        Returns:
            Iterator[PkgbuildPatch]: parsed entries
        """
        return self.parse()
