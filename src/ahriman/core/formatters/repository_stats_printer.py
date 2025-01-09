#
# Copyright (c) 2021-2025 ahriman team.
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
from ahriman.core.utils import pretty_size
from ahriman.models.property import Property
from ahriman.models.repository_id import RepositoryId
from ahriman.models.repository_stats import RepositoryStats


class RepositoryStatsPrinter(StringPrinter):
    """
    print repository statistics

    Attributes:
        statistics(RepositoryStats): repository statistics
    """

    def __init__(self, repository_id: RepositoryId, statistics: RepositoryStats) -> None:
        """
        Args:
            statistics(RepositoryStats): repository statistics
        """
        StringPrinter.__init__(self, str(repository_id))
        self.statistics = statistics

    def properties(self) -> list[Property]:
        """
        convert content into printable data

        Returns:
            list[Property]: list of content properties
        """
        return [
            Property("Packages", self.statistics.bases),
            Property("Repository size", pretty_size(self.statistics.archive_size)),
        ]
