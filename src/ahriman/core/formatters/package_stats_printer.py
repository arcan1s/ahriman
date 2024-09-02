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
from ahriman.core.formatters.string_printer import StringPrinter
from ahriman.models.property import Property


class PackageStatsPrinter(StringPrinter):
    """
    print packages statistics

    Attributes:
        events(dict[str, int]): map of package to its event frequency
    """

    MAX_COUNT = 10

    def __init__(self, events: dict[str, int]) -> None:
        """
        default constructor

        Args:
            events(dict[str, int]): map of package to its event frequency
        """
        StringPrinter.__init__(self, "The most frequent packages")
        self.events = events

    def properties(self) -> list[Property]:
        """
        convert content into printable data

        Returns:
            list[Property]: list of content properties
        """
        if not self.events:
            return []  # no events found, discard any stats

        properties = []
        for object_id, count in sorted(self.events.items(), key=lambda pair: pair[1], reverse=True)[:self.MAX_COUNT]:
            properties.append(Property(object_id, count))

        return properties
