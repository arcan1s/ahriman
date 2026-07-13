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
from ahriman.core.utils import pretty_datetime
from ahriman.models.aur_package import AURPackage
from ahriman.models.property import Property


class AurPrinter(StringPrinter):
    """
    print content of the AUR package

    Attributes:
        package(AURPackage): AUR package description
    """

    def __init__(self, package: AURPackage) -> None:
        """
        Args:
            package(AURPackage): AUR package description
        """
        StringPrinter.__init__(self, f"{package.name} {package.version} ({package.num_votes})")
        self.package = package

    def properties(self) -> list[Property]:
        """
        convert content into printable data

        Returns:
            list[Property]: list of content properties
        """
        return [
            Property("Package base", self.package.package_base),
            Property("Description", self.package.description, is_required=True),
            Property("Upstream URL", self.package.url or ""),
            Property("Licenses", ",".join(self.package.license)),
            Property("Maintainer", self.package.maintainer or ""),
            Property("First submitted", pretty_datetime(self.package.first_submitted)),
            Property("Last updated", pretty_datetime(self.package.last_modified)),
            Property("Keywords", ",".join(self.package.keywords)),
        ]
