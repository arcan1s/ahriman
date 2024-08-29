#
# Copyright (c) 2021-2024 ahriman team.
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
import configparser
import os
import sys

from collections.abc import Generator, Mapping, MutableMapping
from string import Template


class ExtendedTemplate(Template):
    """
    extension to the default :class:`Template` class, which also enabled braces regex to lookup in sections

    Attributes:
        braceidpattern(str): regular expression to match a colon inside braces
    """

    braceidpattern = r"(?a:[_a-z0-9][_a-z0-9:]*)"


class ShellInterpolator(configparser.Interpolation):
    """
    custom string interpolator, because we cannot use defaults argument due to config validation
    """

    DATA_LINK_ESCAPE = "\x10"

    @staticmethod
    def _extract_variables(parser: MutableMapping[str, Mapping[str, str]], value: str,
                           defaults: Mapping[str, str]) -> Generator[tuple[str, str], None, None]:
        """
        extract keys and values (if available) from the configuration. In case if a key is not available, it will be
        silently skipped from the result

        Args:
            parser(MutableMapping[str, Mapping[str, str]]): option parser
            value(str): source (not-converted) value
            defaults(Mapping[str, str]): default values

        Yields:
            tuple[str, str]: variable name used for substitution and its value
        """
        def identifiers() -> Generator[tuple[str | None, str], None, None]:
            # extract all found identifiers and parse them
            for identifier in ExtendedTemplate(value).get_identifiers():
                match identifier.split(":"):
                    case [lookup_option]:  # single option from the same section
                        yield None, lookup_option
                    case [lookup_section, lookup_option]:  # reference to another section
                        yield lookup_section, lookup_option

        for section, option in identifiers():
            # key to be substituted
            key = f"{section}:{option}" if section else option

            if section is not None:  # foreign section case
                if section not in parser:
                    continue  # section was not found, silently skip it
                values = parser[section]
            else:  # same section
                values = defaults

            if (raw := values.get(option)) is not None:
                yield key, raw

    @staticmethod
    def environment() -> dict[str, str]:
        """
        extract environment variables

        Returns:
            dict[str, str]: environment variables and some custom variables
        """
        return os.environ | {
            "prefix": sys.prefix,
        }

    def before_get(self, parser: MutableMapping[str, Mapping[str, str]], section: str, option: str, value: str,
                   defaults: Mapping[str, str]) -> str:
        """
        interpolate option value

        Notes:
            This method is using :class:`string.Template` class in order to render both cross-references and
            environment variables, because it seems that it is the most legit way to handle it. In addition,
            we are using shell-like variables in some cases (see :attr:`alpm.mirror` option),  thus we would like
            to keep them alive.

            First this method resolves substitution from the configuration and then renders environment variables

        Args:
            parser(MutableMapping[str, Mapping[str, str]]): option parser
            section(str): section name
            option(str): option name
            value(str): source (not-converted) value
            defaults(Mapping[str, str]): default values

        Returns:
            str: substituted value
        """
        # because any substitution effectively replace escaped $ ($$) in result, we have to escape it manually
        escaped = value.replace("$$", self.DATA_LINK_ESCAPE)

        # resolve internal references
        variables = dict(self._extract_variables(parser, value, defaults))
        internal = ExtendedTemplate(escaped).safe_substitute(variables)

        # resolve enriched environment variables by using default Template class
        environment = Template(internal).safe_substitute(self.environment())

        # replace escaped values back
        return environment.replace(self.DATA_LINK_ESCAPE, "$")
