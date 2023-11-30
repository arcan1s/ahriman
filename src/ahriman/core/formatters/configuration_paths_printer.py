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
from pathlib import Path

from ahriman.core.formatters.string_printer import StringPrinter
from ahriman.models.property import Property


class ConfigurationPathsPrinter(StringPrinter):
    """
    print configuration paths

    Attributes:
        includes(list[Path]): list of include files
    """

    def __init__(self, root: Path, includes: list[Path]) -> None:
        """
        default constructor

        Args:
            root(Path): path to root configuration file
            includes(list[Path]): list of include files
        """
        StringPrinter.__init__(self, str(root))
        self.includes = includes

    def properties(self) -> list[Property]:
        """
        convert content into printable data

        Returns:
            list[Property]: list of content properties
        """
        return [Property("Include", str(path), is_required=True) for path in self.includes]
