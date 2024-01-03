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

from collections.abc import Mapping, MutableMapping
from string import Template


class ShellInterpolator(configparser.Interpolation):
    """
    custom string interpolator, because we cannot use defaults argument due to config validation
    """

    def before_get(self, parser: MutableMapping[str, Mapping[str, str]], section: str, option: str, value: str,
                   defaults: Mapping[str, str]) -> str:
        """
        interpolate option value

        Args:
            parser(MutableMapping[str, Mapping[str, str]]): option parser
            section(str): section name
            option(str): option name
            value(str): source (not-converted) value
            defaults(Mapping[str, str]): default values

        Returns:
            str: substituted value
        """
        # At the moment it seems that it is the most legit way to handle environment variables
        # Template behaviour is literally the same as shell
        # In addition, we are using shell-like variables in some cases (see :attr:`alpm.mirror` option),
        # thus we would like to keep them alive
        return Template(value).safe_substitute(os.environ)
