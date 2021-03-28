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
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class PackageDescription:
    """
    package specific properties
    :ivar archive_size: package archive size
    :ivar build_date: package build date
    :ivar filename: package archive name
    :ivar installed_size: package installed size
    """

    archive_size: Optional[int] = None
    build_date: Optional[int] = None
    filename: Optional[str] = None
    installed_size: Optional[int] = None

    @property
    def filepath(self) -> Optional[Path]:
        """
        :return: path object for current filename
        """
        return Path(self.filename) if self.filename is not None else None
