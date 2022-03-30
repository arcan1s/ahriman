#
# Copyright (c) 2021-2022 ahriman team.
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
from typing import Callable, List, Optional

from ahriman.models.property import Property


class Printer:
    """
    base class for formatters
    """

    def print(self, verbose: bool, log_fn: Callable[[str], None] = print, separator: str = ": ") -> None:
        """
        print content
        :param verbose: print all fields
        :param log_fn: logger function to log data
        :param separator: separator for property name and property value
        """
        if (title := self.title()) is not None:
            log_fn(title)
        for prop in self.properties():
            if not verbose and not prop.is_required:
                continue
            log_fn(f"\t{prop.name}{separator}{prop.value}")

    def properties(self) -> List[Property]:  # pylint: disable=no-self-use
        """
        convert content into printable data
        :return: list of content properties
        """
        return []

    def title(self) -> Optional[str]:
        """
        generate entry title from content
        :return: content title if it can be generated and None otherwise
        """
