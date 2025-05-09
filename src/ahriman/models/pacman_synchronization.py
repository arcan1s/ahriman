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
from enum import IntEnum


class PacmanSynchronization(IntEnum):
    """
    pacman database synchronization flag

    Attributes:
        Disabled(PacmanSynchronization): do not synchronize local database
        Enabled(PacmanSynchronization): synchronize local database (same as pacman -Sy)
        Force(PacmanSynchronization): force synchronize local database (same as pacman -Syy)
    """

    Disabled = 0
    Enabled = 1
    Force = 2
