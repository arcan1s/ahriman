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
import argparse
import re
import textwrap


class _HelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    """
    :class:`argparse.ArgumentDefaultsHelpFormatter` extension which keeps new lines in help messages
    """

    def __init__(self, prog: str) -> None:
        """
        Args:
            prog(str): application name
        """
        argparse.ArgumentDefaultsHelpFormatter.__init__(self, prog, width=120)
        self._whitespace_matcher = re.compile(r"[ \t]+")

    def _fill_text(self, text: str, width: int, indent: str) -> str:
        """
        implementation of the protected method to format text. Format text, keeping new lines

        Args:
            text(str): text to format
            width(int): maximal text width
            indent(str): indentation string

        Returns:
            str: formatted text
        """
        text = self._whitespace_matcher.sub(" ", text).strip()
        return "\n".join([
            textwrap.fill(line, width, initial_indent=indent, subsequent_indent=indent)
            for line in text.splitlines()
        ])
