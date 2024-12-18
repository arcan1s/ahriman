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
import statistics

from ahriman.core.formatters.string_printer import StringPrinter
from ahriman.core.utils import minmax
from ahriman.models.property import Property


class EventStatsPrinter(StringPrinter):
    """
    print event statistics

    Attributes:
        events(list[float | int]): event values to build statistics
    """

    def __init__(self, event_type: str, events: list[float | int]) -> None:
        """
        Args:
            event_type(str): event type used for this statistics
            events(list[float | int]): event values to build statistics
        """
        StringPrinter.__init__(self, event_type)
        self.events = events

    def properties(self) -> list[Property]:
        """
        convert content into printable data

        Returns:
            list[Property]: list of content properties
        """
        properties = [
            Property("total", len(self.events)),
        ]

        # time statistics
        if self.events:
            min_time, max_time = minmax(self.events)
            mean = statistics.mean(self.events)

            if len(self.events) > 1:
                st_dev = statistics.stdev(self.events)
                average = f"{mean:.3f} ± {st_dev:.3f}"
            else:
                average = f"{mean:.3f}"

            properties.extend([
                Property("min", min_time),
                Property("average", average),
                Property("max", max_time),
            ])

        return properties
