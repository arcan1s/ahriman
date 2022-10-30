#
# Copyright (c) 2021-2022 ahriman team.
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
from typing import List

from ahriman.core.formatters import StringPrinter
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.property import Property


class PatchPrinter(StringPrinter):
    """
    print content of the PKGBUILD patch

    Attributes:
        patches(List[PkgbuildPatch]): PKGBUILD patch object
    """

    def __init__(self, package_base: str, patches: List[PkgbuildPatch]) -> None:
        """
        default constructor

        Args:
            package_base(str): package base
            patches(List[PkgbuildPatch]): PKGBUILD patch object
        """
        StringPrinter.__init__(self, package_base)
        self.patches = patches

    def properties(self) -> List[Property]:
        """
        convert content into printable data

        Returns:
            List[Property]: list of content properties
        """
        return [
            Property(patch.key or "Full source diff", patch.value, is_required=True)
            for patch in self.patches
        ]
