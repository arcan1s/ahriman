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
from sqlite3 import Connection
from typing import Dict, Optional

from ahriman.core.database.operations.operations import Operations


class PatchOperations(Operations):
    """
    operations for patches
    """

    def patches_get(self, package_base: str) -> Optional[str]:
        """
        retrieve patches for the package
        :param package_base: package base to search for patches
        :return: plain text patch for the package
        """
        return self.patches_list(package_base).get(package_base)

    def patches_insert(self, package_base: str, patch: str) -> None:
        """
        insert or update patch in database
        :param package_base: package base to insert
        :param patch: patch content
        """
        def run(connection: Connection) -> None:
            connection.execute(
                """
                insert into patches
                (package_base, patch)
                values
                (:package_base, :patch)
                on conflict (package_base) do update set
                patch = :patch
                """,
                {"package_base": package_base, "patch": patch})

        return self.with_connection(run, commit=True)

    def patches_list(self, package_base: Optional[str]) -> Dict[str, str]:
        """
        extract all patches
        :param package_base: optional filter by package base
        :return: map of package base to patch content
        """
        def run(connection: Connection) -> Dict[str, str]:
            return {
                cursor["package_base"]: cursor["patch"]
                for cursor in connection.execute(
                    """select * from patches where :package_base is null or package_base = :package_base""",
                    {"package_base": package_base})
            }

        return self.with_connection(run)

    def patches_remove(self, package_base: str) -> None:
        """
        remove patch set
        :param package_base: package base to clear patches
        """
        def run(connection: Connection) -> None:
            connection.execute(
                """delete from patches where package_base = :package_base""",
                {"package_base": package_base})

        return self.with_connection(run, commit=True)
