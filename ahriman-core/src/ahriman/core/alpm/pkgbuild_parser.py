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
import shlex
import tree_sitter_bash

from collections.abc import Iterable, Iterator
from enum import StrEnum
from tree_sitter import Language, Node, Parser
from typing import IO, cast

from ahriman.core.configuration.shell_interpolator import ShellInterpolator
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

    _ESCAPED_CHARACTERS = {
        "\\$": "$",
        "\\`": "`",
        "\\\"": "\"",
        "\\\n": "",
    }

    def __init__(self, stream: IO[bytes]) -> None:
        """
        Args:
            stream(IO[bytes]): input PKGBUILD stream
        """
        self._content = stream.read()

    @staticmethod
    def text(node: Node) -> str:
        """
        read the original source text represented by a syntax tree node

        Args:
            node(Node): syntax tree node to read

        Returns:
            str: source text for the node
        """
        return cast(bytes, node.text).decode("utf8", errors="backslashreplace")

    @staticmethod
    def unquote(value: str) -> str:
        """
        remove shell quotes and escapes from a single value

        Args:
            value(str): shell value to unquote

        Returns:
            str: unquoted value
        """
        return "".join(shlex.split(value, comments=False, posix=True))

    @staticmethod
    def value(node: Node) -> str:
        """
        extract a string value from a syntax tree node

        Args:
            node(Node): syntax tree node to extract

        Returns:
            str: extracted string value
        """
        def unescape(source: str) -> str:
            for original, replacement in PkgbuildParser._ESCAPED_CHARACTERS.items():
                source = source.replace(original, replacement)
            return source

        if node.type == PkgbuildNodeType.Concatenation:
            return "".join(PkgbuildParser.value(child) for child in node.named_children)

        value = PkgbuildParser.text(node)
        match node.type:
            case PkgbuildNodeType.String | PkgbuildNodeType.StringContent:
                if node.type == PkgbuildNodeType.String:
                    value = PkgbuildParser.unquote(value)
                # protect escaped backslashes from being interpreted a second time.
                return "\\".join(unescape(part) for part in value.split("\\\\"))
            case PkgbuildNodeType.Number | PkgbuildNodeType.RawString | PkgbuildNodeType.Word:
                return PkgbuildParser.unquote(value)
            case _:
                return value

    def _assignment(self, node: Node) -> PkgbuildPatch:
        """
        convert an assignment node

        Args:
            node(Node): assignment node to convert

        Returns:
            PkgbuildPatch: parsed assignment
        """
        key = self.text(cast(Node, node.child_by_field_name(PkgbuildNodeField.Name)))
        value = node.child_by_field_name(PkgbuildNodeField.Value)
        # bash permits assignments without a value (for example ``IFS=``).
        # tree-sitter represents those assignments without a value node.
        if value is None:
            return PkgbuildPatch(key, "")

        match value.type:
            case PkgbuildNodeType.Array:
                values = []
                for element in filter(lambda child: child.type != PkgbuildNodeType.Comment, value.named_children):
                    values.extend(self._expand_array(element))
                return PkgbuildPatch(key, values)

            case _:
                return PkgbuildPatch(key, self.value(value))

    def _expand_array(self, node: Node) -> list[str]:
        """
        expand simple comma-separated brace groups in an array element

        Args:
            node(Node): array element to expand

        Returns:
            list[str]: expanded element values
        """
        if node.type != PkgbuildNodeType.Concatenation:
            return [self.value(node)]

        values = [""]
        children = node.named_children
        while children:
            match children[:3]:
                case [
                    Node(type=PkgbuildNodeType.Word, text=b"{"),
                    Node(type=PkgbuildNodeType.Word) as content,
                    Node(type=PkgbuildNodeType.Word, text=b"}"),
                ] if "," in (escaped := self.text(content).replace("\\,", ShellInterpolator.DATA_LINK_ESCAPE)):
                    parts = [
                        self.unquote(part).replace(ShellInterpolator.DATA_LINK_ESCAPE, ",")
                        for part in escaped.split(",")
                    ]
                    children = children[3:]

                case _:
                    parts = [self.value(children.pop(0))]

            values = [prefix + part for prefix in values for part in parts]

        return values

    def _read(self, node: Node, values: dict[str | None, PkgbuildPatch]) -> Iterator[PkgbuildPatch]:
        """
        find assignments and functions in a syntax tree node

        Args:
            node(Node): syntax tree node to inspect
            values(dict[str | None, PkgbuildPatch]): cached assignments

        Yields:
            PkgbuildPatch: parsed entries
        """
        match node.type:
            case PkgbuildNodeType.VariableAssignment if any(child.type == PkgbuildNodeType.Append for child in node.children):
                patch = self._assignment(node)
                match values.get(patch.key), patch.value:
                    case PkgbuildPatch(value=str() as previous), str() as appended:
                        patch = PkgbuildPatch(patch.key, previous + appended)
                    case PkgbuildPatch(value=str() as previous), list() as appended:
                        patch = PkgbuildPatch(patch.key, [previous, *appended])
                    case PkgbuildPatch(value=list() as previous), list() as appended:
                        patch = PkgbuildPatch(patch.key, previous + appended)
                values[patch.key] = patch
                yield patch

            case PkgbuildNodeType.VariableAssignment:
                patch = self._assignment(node)
                values[patch.key] = patch
                yield patch

            case PkgbuildNodeType.FunctionDefinition:
                name = cast(Node, node.child_by_field_name(PkgbuildNodeField.Name))
                body = cast(Node, node.child_by_field_name(PkgbuildNodeField.Body))
                yield PkgbuildPatch(f"{self.text(name)}()", self.text(body))

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
                        yield from self._read(child, values)

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

        yield from self._read(tree.root_node, {})

    def __iter__(self) -> Iterator[PkgbuildPatch]:
        """
        iterate over the parsed entries

        Returns:
            Iterator[PkgbuildPatch]: parsed entries
        """
        return self.parse()
