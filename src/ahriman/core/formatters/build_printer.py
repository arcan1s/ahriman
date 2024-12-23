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
from ahriman.models.package import Package


class BuildPrinter(StringPrinter):
    """
    print content of the build result
    """

    def __init__(self, package: Package, is_success: bool, use_utf: bool) -> None:
        """
        Args:
            package(Package): built package
            is_success(bool): ``True`` in case if build has success status and ``False`` otherwise
            use_utf(bool): use utf instead of normal symbols
        """
        StringPrinter.__init__(self, f"{self.sign(is_success, use_utf)} {package.base}")

    @staticmethod
    def sign(is_success: bool, use_utf: bool) -> str:
        """
        generate sign according to settings

        Args:
            is_success(bool): ``True`` in case if build has success status and ``False`` otherwise
            use_utf(bool): use utf instead of normal symbols

        Returns:
            str: sign symbol according to current settings
        """
        if is_success:
            return "[✔]" if use_utf else "[x]"
        return "[❌]" if use_utf else "[ ]"
