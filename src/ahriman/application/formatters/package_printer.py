#
# Copyright (c) 2021 ahriman team.
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
from typing import List, Optional

from ahriman.application.formatters.printer import Printer
from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package
from ahriman.models.property import Property


class PackagePrinter(Printer):
    """
    print content of the internal package object
    """

    def __init__(self, package: Package, status: BuildStatus) -> None:
        """
        default constructor
        :param package: package description
        :param status: build status
        """
        self.content = package
        self.status = status

    def properties(self) -> List[Property]:
        """
        convert content into printable data
        :return: list of content properties
        """
        return [
            Property("Version", self.content.version, is_required=True),
            Property("Groups", " ".join(self.content.groups)),
            Property("Licenses", " ".join(self.content.licenses)),
            Property("Depends", " ".join(self.content.depends)),
            Property("Status", self.status.pretty_print(), is_required=True),
        ]

    def title(self) -> Optional[str]:
        """
        generate entry title from content
        :return: content title if it can be generated and None otherwise
        """
        return self.content.pretty_print()
