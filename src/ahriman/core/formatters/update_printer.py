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
from ahriman.core.formatters.string_printer import StringPrinter
from ahriman.models.package import Package
from ahriman.models.property import Property


class UpdatePrinter(StringPrinter):
    """
    print content of the package update

    Attributes:
        package(Package): remote (new) package object
        local_version(str | None): local version of the package if any
    """

    def __init__(self, remote: Package, local_version: str | None) -> None:
        """
        default constructor

        Args:
            remote(Package): remote (new) package object
            local_version(str | None): local version of the package if any
        """
        StringPrinter.__init__(self, remote.base)
        self.package = remote
        self.local_version = local_version or "N/A"

    def properties(self) -> list[Property]:
        """
        convert content into printable data

        Returns:
            list[Property]: list of content properties
        """
        return [Property(self.local_version, self.package.version, is_required=True)]
