#
# Copyright (c) 2021-2026 ahriman team.
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
from ahriman.models.changes import Changes
from ahriman.models.repository_id import RepositoryId


class ChangesOperations(Operations):
    """
    operations for source files changes
    """

    def changes_get(self, package_base: str, repository_id: RepositoryId | None = None) -> Changes:
        """
        get changes for the specific package base if available

        Args:
            package_base(str): package base to search
            repository_id(RepositoryId, optional): repository unique identifier override (Default value = None)

        Returns:
            Changes: changes for the package base if available
        """
        repository_id = repository_id or self._repository_id

        def run(connection: Connection) -> Changes:
            return next(
                (
                    Changes(row["last_commit_sha"], row["changes"] or None)
                    for row in connection.execute(
                        """
                        select last_commit_sha, changes from package_changes
                        where package_base = :package_base and repository = :repository
                        """,
                        {
                            "package_base": package_base,
                            "repository": repository_id.id,
                        }
                    )
                ),
                Changes()
            )

        return self.with_connection(run)

    def changes_insert(self, package_base: str, changes: Changes, repository_id: RepositoryId | None = None) -> None:
        """
        insert package changes

        Args:
            package_base(str): package base to insert
            changes(Changes): package changes (as in patch format)
            repository_id(RepositoryId, optional): repository unique identifier override (Default value = None)
        """
        repository_id = repository_id or self._repository_id

        def run(connection: Connection) -> None:
            connection.execute(
                """
                insert into package_changes
                (package_base, last_commit_sha, changes, repository)
                values
                (:package_base, :last_commit_sha, :changes ,:repository)
                on conflict (package_base, repository) do update set
                last_commit_sha = :last_commit_sha, changes = :changes
                """,
                {
                    "package_base": package_base,
                    "last_commit_sha": changes.last_commit_sha,
                    "changes": changes.changes,
                    "repository": repository_id.id,
                })

        if changes.last_commit_sha is None:
            return self.changes_remove(package_base, repository_id)
        return self.with_connection(run, commit=True)

    def changes_remove(self, package_base: str | None, repository_id: RepositoryId | None = None) -> None:
        """
        remove packages changes

        Args:
            package_base(str | None): optional filter by package base
            repository_id(RepositoryId, optional): repository unique identifier override (Default value = None)
        """
        repository_id = repository_id or self._repository_id

        def run(connection: Connection) -> None:
            connection.execute(
                """
                delete from package_changes
                where (:package_base is null or package_base = :package_base)
                  and repository = :repository
                """,
                {
                    "package_base": package_base,
                    "repository": repository_id.id,
                })

        return self.with_connection(run, commit=True)
