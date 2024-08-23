#
# Copyright (c) 2021-2024 ahriman team.
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

from ahriman.core.database.operations.operations import Operations
from ahriman.models.dependencies import Dependencies
from ahriman.models.repository_id import RepositoryId


class DependenciesOperations(Operations):
    """
    operations for dependencies table
    """

    def dependencies_get(self, package_base: str | None = None,
                         repository_id: RepositoryId | None = None) -> dict[str, Dependencies]:
        """
        get dependencies for the specific package base if available

        Args:
            package_base(str | None): package base to search
            repository_id(RepositoryId, optional): repository unique identifier override (Default value = None)

        Returns:
            Dependencies: dependencies for the package base if available
        """
        repository_id = repository_id or self._repository_id

        def run(connection: Connection) -> dict[str, Dependencies]:
            return {
                row["package_base"]: Dependencies(row["dependencies"])
                for row in connection.execute(
                    """
                        select package_base, dependencies from package_dependencies
                        where (:package_base is null or package_base = :package_base)
                          and repository = :repository
                        """,
                    {
                        "package_base": package_base,
                        "repository": repository_id.id,
                    }
                )
            }

        return self.with_connection(run)

    def dependencies_insert(self, package_base: str, dependencies: Dependencies,
                            repository_id: RepositoryId | None = None) -> None:
        """
        insert package dependencies

        Args:
            package_base(str): package base
            dependencies(Dependencies): package dependencies
            repository_id(RepositoryId, optional): repository unique identifier override (Default value = None)
        """
        repository_id = repository_id or self._repository_id

        def run(connection: Connection) -> None:
            connection.execute(
                """
                insert into package_dependencies
                (package_base, repository, dependencies)
                values
                (:package_base, :repository, :dependencies)
                on conflict (package_base, repository) do update set
                dependencies = :dependencies
                """,
                {
                    "package_base": package_base,
                    "repository": repository_id.id,
                    "dependencies": dependencies.paths,
                })

        return self.with_connection(run, commit=True)

    def dependencies_remove(self, package_base: str | None, repository_id: RepositoryId | None = None) -> None:
        """
        remove packages dependencies

        Args:
            package_base(str | None): optional filter by package base
            repository_id(RepositoryId, optional): repository unique identifier override (Default value = None)
        """
        repository_id = repository_id or self._repository_id

        def run(connection: Connection) -> None:
            connection.execute(
                """
                delete from package_dependencies
                where (:package_base is null or package_base = :package_base)
                  and repository = :repository
                """,
                {
                    "package_base": package_base,
                    "repository": repository_id.id,
                })

        return self.with_connection(run, commit=True)
