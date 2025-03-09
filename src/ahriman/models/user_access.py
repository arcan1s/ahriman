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
from __future__ import annotations

from enum import StrEnum


class UserAccess(StrEnum):
    """
    web user access enumeration

    Attributes:
        Unauthorized(UserAccess): user can access specific resources which are marked as available
            without authorization (e.g. login, logout, static)
        Read(UserAccess): user can read the page
        Reporter(UserAccess): user can read everything and is able to perform some modifications
        Full(UserAccess): user has full access
    """

    Unauthorized = "unauthorized"
    Read = "read"
    Reporter = "reporter"
    Full = "full"

    def permits(self, other: UserAccess) -> bool:
        """
        compare enumeration between each other and check if current permission allows the ``other``

        Args:
            other(UserAccess): other permission to compare

        Returns:
            bool: ``True`` in case if current permission allows the operation and ``False`` otherwise
        """
        for member in UserAccess:
            if member == other:
                return True
            if member == self:
                return False
        return False  # must never happen
