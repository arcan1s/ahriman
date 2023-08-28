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
from sqlite3 import Connection

from ahriman.core.database.operations import Operations
from ahriman.models.package import Package


class BuildOperations(Operations):
    """
    operations for build queue functions
    """

    def build_queue_clear(self, package_base: str | None) -> None:
        """
        remove packages from build queue

        Args:
            package_base(str | None): optional filter by package base
        """
        def run(connection: Connection) -> None:
            connection.execute(
                """
                delete from build_queue
                where (:package_base is null or package_base = :package_base) and repository = :repository
                """,
                {"package_base": package_base, "repository": self.repository_id.name})

        return self.with_connection(run, commit=True)

    def build_queue_get(self) -> list[Package]:
        """
        retrieve packages from build queue

        Return:
            list[Package]: list of packages to be built
        """
        def run(connection: Connection) -> list[Package]:
            return [
                Package.from_json(row["properties"])
                for row in connection.execute(
                    """select properties from build_queue where repository = :repository""",
                    {"repository": self.repository_id.name}
                )
            ]

        return self.with_connection(run)

    def build_queue_insert(self, package: Package) -> None:
        """
        insert packages to build queue

        Args:
            package(Package): package to be inserted
        """
        def run(connection: Connection) -> None:
            connection.execute(
                """
                insert into build_queue
                (package_base, properties, repository)
                values
                (:package_base, :properties, :repository)
                on conflict (package_base, repository) do update set
                properties = :properties
                """,
                {"package_base": package.base, "properties": package.view(), "repository": self.repository_id.name})

        return self.with_connection(run, commit=True)
