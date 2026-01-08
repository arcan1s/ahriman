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
import fnmatch
import re

from collections.abc import Generator, Mapping
from string import Template


class ShellTemplate(Template):
    """
    extension to the default :class:`Template` class, which also adds additional tokens to braced regex and enables
    bash expansion
    """

    braceidpattern = r"(?a:[_a-z0-9][^}]*)"

    _REMOVE_BACK = re.compile(r"^(?P<key>\w+)%(?P<pattern>.+)$")
    _REMOVE_FRONT = re.compile(r"^(?P<key>\w+)#(?P<pattern>.+)$")
    _REPLACE = re.compile(r"^(?P<key>\w+)/(?P<pattern>.+)/(?P<replacement>.+)$")

    @staticmethod
    def _remove_back(source: str, pattern: str, *, greedy: bool) -> str:
        """
        resolve "${var%(%)pattern}" constructions

        Args:
            source(str): source string to match the pattern inside
            pattern(str): shell expression to match
            greedy(bool): match as much as possible or not

        Returns:
            str: result after removal ``pattern`` from the end of the string
        """
        regex = fnmatch.translate(pattern)
        compiled = re.compile(regex)

        result = source
        start_pos = 0

        while m := compiled.search(source, start_pos):
            result = source[:m.start()]
            start_pos += m.start() + 1
            if greedy:
                break

        return result

    @staticmethod
    def _remove_front(source: str, pattern: str, *, greedy: bool) -> str:
        """
        resolve "${var#(#)pattern}" constructions

        Args:
            source(str): source string to match the pattern inside
            pattern(str): shell expression to match
            greedy(bool): match as much as possible or not

        Returns:
            str: result after removal ``pattern`` from the start of the string
        """
        regex = fnmatch.translate(pattern)[:-2]  # remove \Z at the end of the regex
        if not greedy:
            regex = regex.replace("*", "*?")
        compiled = re.compile(regex)

        m = compiled.match(source)
        if m is None:
            return source

        return source[m.end():]

    @staticmethod
    def _replace(source: str, pattern: str, replacement: str, *, greedy: bool) -> str:
        """
        resolve "${var/(/)pattern/replacement}" constructions

        Args:
            source(str): source string to match the pattern inside
            pattern(str): shell expression to match
            replacement(str): new substring
            greedy(bool): replace as much as possible or not

        Returns:
            str: result after replacing ``pattern`` by ``replacement``
        """
        match pattern:
            case from_back if from_back.startswith("%"):
                removed = ShellTemplate._remove_back(source, from_back[1:], greedy=False)
                return removed if removed == source else removed + replacement

            case from_front if from_front.startswith("#"):
                removed = ShellTemplate._remove_front(source, from_front[1:], greedy=False)
                return removed if removed == source else replacement + removed

            case regular:
                regex = fnmatch.translate(regular)[:-2]  # remove \Z at the end of the regex
                compiled = re.compile(regex)
                return compiled.sub(replacement, source, count=not greedy)

    def shell_substitute(self, mapping: Mapping[str, str], /, **kwargs: str) -> str:
        """
        this method behaves the same as :func:`safe_substitute`, however also expands bash string operations

        Args:
            mapping(Mapping[str, str]): key-value dictionary of variables
            **kwargs(str): key-value dictionary of variables passed as kwargs

        Returns:
            str: string with replaced values
        """
        substitutions = (
            (self._REMOVE_BACK, self._remove_back, "%"),
            (self._REMOVE_FRONT, self._remove_front, "#"),
            (self._REPLACE, self._replace, "/"),
        )

        def generator(variables: dict[str, str]) -> Generator[tuple[str, str], None, None]:
            for identifier in self.get_identifiers():
                for regex, function, greediness in substitutions:
                    if m := regex.match(identifier):
                        source = variables.get(m.group("key"))
                        if source is None:
                            continue

                        # replace pattern with non-greedy
                        pattern = m.group("pattern").removeprefix(greediness)
                        greedy = m.group("pattern").startswith(greediness)
                        # gather all additional args
                        args = {key: value for key, value in m.groupdict().items() if key not in ("key", "pattern")}

                        yield identifier, function(source, pattern, **args, greedy=greedy)
                        break

        kwargs.update(mapping)
        substituted = dict(generator(kwargs))

        return self.safe_substitute(kwargs | substituted)
