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
from dataclasses import dataclass

from ahriman.core.exceptions import MigrationError


@dataclass(frozen=True, kw_only=True)
class MigrationResult:
    """
    migration result implementation model

    Attributes:
        old_version(int): old schema version before migrations
        new_version(int): new schema version after migrations
    """

    old_version: int
    new_version: int

    @property
    def is_outdated(self) -> bool:
        """
        check migration and check if there are pending migrations

        Returns:
            bool: True in case if it requires migrations and False otherwise
        """
        self.validate()
        return self.new_version > self.old_version

    def validate(self) -> None:
        """
        perform version validation

        Raises:
            MigrationError: if old version is newer than new one or negative
        """
        if self.old_version < 0 or self.old_version > self.new_version:
            raise MigrationError(f"Invalid current schema version, expected less or equal to {self.new_version}, "
                                 f"got {self.old_version}")
