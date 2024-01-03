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
from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package
from ahriman.models.property import Property


class PackagePrinter(StringPrinter):
    """
    print content of the internal package object

    Attributes:
        package(Package): package description
        status(BuildStatus): build status
    """

    def __init__(self, package: Package, status: BuildStatus) -> None:
        """
        default constructor

        Args:
            package(Package): package description
            status(BuildStatus): build status
        """
        StringPrinter.__init__(self, package.pretty_print())
        self.package = package
        self.status = status

    def properties(self) -> list[Property]:
        """
        convert content into printable data

        Returns:
            list[Property]: list of content properties
        """
        return [
            Property("Version", self.package.version, is_required=True),
            Property("Groups", " ".join(self.package.groups)),
            Property("Licenses", " ".join(self.package.licenses)),
            Property("Depends", " ".join(self.package.depends)),
            Property("Status", self.status.pretty_print(), is_required=True),
        ]
