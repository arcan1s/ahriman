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
from collections import defaultdict

from sqlite3 import Connection
from typing import Dict, List, Optional, Tuple

from ahriman.core.database.operations import Operations
from ahriman.models.pkgbuild_patch import PkgbuildPatch


class PatchOperations(Operations):
    """
    operations for patches
    """

    def patches_get(self, package_base: str) -> List[PkgbuildPatch]:
        """
        retrieve patches for the package

        Args:
            package_base(str): package base to search for patches

        Returns:
            List[PkgbuildPatch]: plain text patch for the package
        """
        return self.patches_list(package_base, []).get(package_base, [])

    def patches_insert(self, package_base: str, patch: PkgbuildPatch) -> None:
        """
        insert or update patch in database

        Args:
            package_base(str): package base to insert
            patch(PkgbuildPatch): patch content
        """
        def run(connection: Connection) -> None:
            connection.execute(
                """
                insert into patches
                (package_base, variable, patch)
                values
                (:package_base, :variable, :patch)
                on conflict (package_base, coalesce(variable, '')) do update set
                patch = :patch
                """,
                {"package_base": package_base, "variable": patch.key, "patch": patch.value})

        return self.with_connection(run, commit=True)

    def patches_list(self, package_base: Optional[str], variables: List[str]) -> Dict[str, List[PkgbuildPatch]]:
        """
        extract all patches

        Args:
            package_base(Optional[str]): optional filter by package base
            variables(List[str]): extract patches only for specified PKGBUILD variables

        Returns:
            Dict[str, List[PkgbuildPatch]]: map of package base to patch content
        """
        def run(connection: Connection) -> List[Tuple[str, PkgbuildPatch]]:
            return [
                (cursor["package_base"], PkgbuildPatch(cursor["variable"], cursor["patch"]))
                for cursor in connection.execute(
                    """select * from patches where :package_base is null or package_base = :package_base""",
                    {"package_base": package_base})
            ]

        # we could use itertools & operator but why?
        patches: Dict[str, List[PkgbuildPatch]] = defaultdict(list)
        for package, patch in self.with_connection(run):
            if variables and patch.key not in variables:
                continue
            patches[package].append(patch)
        return dict(patches)

    def patches_remove(self, package_base: str, variables: List[str]) -> None:
        """
        remove patch set

        Args:
            package_base(str): package base to clear patches
            variables(List[str]): remove patches only for specified PKGBUILD variables
        """
        def run_many(connection: Connection) -> None:
            connection.executemany(
                """delete from patches where package_base = :package_base and variable = :variable""",
                [{"package_base": package_base, "variable": variable} for variable in variables])

        def run(connection: Connection) -> None:
            connection.execute(
                """delete from patches where package_base = :package_base""",
                {"package_base": package_base})

        if variables:
            return self.with_connection(run_many, commit=True)
        return self.with_connection(run, commit=True)
