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
from ahriman.core.util import pretty_datetime
from ahriman.models.aur_package import AURPackage
from ahriman.models.property import Property


class AurPrinter(Printer):
    """
    print content of the AUR package
    """

    def __init__(self, package: AURPackage) -> None:
        """
        default constructor
        :param package: AUR package description
        """
        self.content = package

    def properties(self) -> List[Property]:
        """
        convert content into printable data
        :return: list of content properties
        """
        return [
            Property("Package base", self.content.package_base),
            Property("Description", self.content.description, is_required=True),
            Property("Upstream URL", self.content.url or ""),
            Property("Licenses", ",".join(self.content.license)),
            Property("Maintainer", self.content.maintainer or ""),
            Property("First submitted", pretty_datetime(self.content.first_submitted)),
            Property("Last updated", pretty_datetime(self.content.last_modified)),
            Property("Keywords", ",".join(self.content.keywords)),
        ]

    def title(self) -> Optional[str]:
        """
        generate entry title from content
        :return: content title if it can be generated and None otherwise
        """
        return f"{self.content.name} {self.content.version} ({self.content.num_votes})"
