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
from ahriman.core.formatters.printer import Printer


class StringPrinter(Printer):
    """
    print content of the random string

    Attributes:
        content(str): any content string
    """

    def __init__(self, content: str) -> None:
        """
        Args:
            content(str): any content string
        """
        self.content = content

    def title(self) -> str | None:
        """
        generate entry title from content

        Returns:
            str | None: content title if it can be generated and ``None`` otherwise
        """
        return self.content
