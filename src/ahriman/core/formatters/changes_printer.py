#
# Copyright (c) 2021-2023 ahriman team.
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
from ahriman.core.formatters import Printer
from ahriman.models.changes import Changes
from ahriman.models.property import Property


class ChangesPrinter(Printer):
    """
    print content of the changes object

    Attributes:
        changes(Changes): package changes
    """

    def __init__(self, changes: Changes) -> None:
        """
        default constructor

        Args:
            changes(Changes): package changes
        """
        Printer.__init__(self)
        self.changes = changes

    def properties(self) -> list[Property]:
        """
        convert content into printable data

        Returns:
            list[Property]: list of content properties
        """
        if self.changes.is_empty:
            return []
        return [Property("", self.changes.changes, is_required=True, indent=0)]

    # pylint: disable=redundant-returns-doc
    def title(self) -> str | None:
        """
        generate entry title from content

        Returns:
            str | None: content title if it can be generated and None otherwise
        """
        if self.changes.is_empty:
            return None
        return self.changes.last_commit_sha
