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
from ahriman.core.formatters.string_printer import StringPrinter
from ahriman.models.property import Property
from ahriman.models.repository_id import RepositoryId


class RepositoryPrinter(StringPrinter):
    """
    print repository unique identifier

    Attributes:
        repository_id(RepositoryId): repository unique identifier
    """

    def __init__(self, repository_id: RepositoryId) -> None:
        """
        Args:
            repository_id(RepositoryId): repository unique identifier
        """
        StringPrinter.__init__(self, repository_id.id)
        self.repository_id = repository_id

    def properties(self) -> list[Property]:
        """
        convert content into printable data

        Returns:
            list[Property]: list of content properties
        """
        return [
            Property("Name", self.repository_id.name),
            Property("Architecture", self.repository_id.architecture),
        ]
