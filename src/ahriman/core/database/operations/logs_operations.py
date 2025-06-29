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
from sqlite3 import Connection

from ahriman.core.database.operations.operations import Operations
from ahriman.models.log_record import LogRecord
from ahriman.models.repository_id import RepositoryId


class LogsOperations(Operations):
    """
    logs operations
    """

    def logs_get(self, package_base: str, version: str | None = None, process_id: str | None = None,
                 limit: int = -1, offset: int = 0, repository_id: RepositoryId | None = None) -> list[LogRecord]:
        """
        extract logs for specified package base

        Args:
            package_base(str): package base to extract logs
            version(str | None, optional): package version to filter (Default value = None)
            process_id(str | None, optional): process identifier to filter (Default value = None)
            limit(int, optional): limit records to the specified count, -1 means unlimited (Default value = -1)
            offset(int, optional): records offset (Default value = 0)
            repository_id(RepositoryId, optional): repository unique identifier override (Default value = None)

        Return:
            list[LogRecord]: sorted package log records
        """
        repository_id = repository_id or self._repository_id

        def run(connection: Connection) -> list[LogRecord]:
            return [
                LogRecord.from_json(package_base, row)
                for row in connection.execute(
                    """
                    select created, message, version, process_id from (
                        select * from logs
                        where package_base = :package_base
                          and repository = :repository
                          and (:version is null or version = :version)
                          and (:process_id is null or process_id = :process_id)
                        order by created desc limit :limit offset :offset
                    ) order by created asc
                    """,
                    {
                        "package_base": package_base,
                        "version": version,
                        "process_id": process_id,
                        "repository": repository_id.id,
                        "limit": limit,
                        "offset": offset,
                    })
            ]

        return self.with_connection(run)

    def logs_insert(self, log_record: LogRecord, repository_id: RepositoryId | None = None) -> None:
        """
        write new log record to database

        Args:
            log_record(LogRecord): log record object
            repository_id(RepositoryId, optional): repository unique identifier override (Default value = None)
        """
        repository_id = repository_id or self._repository_id

        def run(connection: Connection) -> None:
            connection.execute(
                """
                insert into logs
                (package_base, version, created, message, repository, process_id)
                values
                (:package_base, :version, :created, :message, :repository, :process_id)
                """,
                {
                    "package_base": log_record.log_record_id.package_base,
                    "repository": repository_id.id,
                } | log_record.view()
            )

        return self.with_connection(run, commit=True)

    def logs_remove(self, package_base: str, version: str | None, repository_id: RepositoryId | None = None) -> None:
        """
        remove log records for the specified package

        Args:
            package_base(str): package base to remove logs
            version(str | None): package version. If set it will remove only logs belonging to another version
            repository_id(RepositoryId, optional): repository unique identifier override (Default value = None)
        """
        repository_id = repository_id or self._repository_id

        def run(connection: Connection) -> None:
            connection.execute(
                """
                delete from logs
                where package_base = :package_base
                  and repository = :repository
                  and (:version is null or version <> :version)
                """,
                {
                    "package_base": package_base,
                    "version": version,
                    "repository": repository_id.id,
                }
            )

        return self.with_connection(run, commit=True)

    def logs_rotate(self, keep_last_records: int, repository_id: RepositoryId | None = None) -> None:
        """
        rotate logs in storage. This method will remove old logs, keeping only the last N records for each package

        Args:
            keep_last_records(int): number of last records to keep
            repository_id(RepositoryId, optional): repository unique identifier override (Default value = None)
        """
        repository_id = repository_id or self._repository_id

        def remove_duplicates(connection: Connection) -> None:
            connection.execute(
                """
                delete from logs
                where (package_base, version, repository, process_id) not in (
                  select package_base, version, repository, process_id from logs
                  where (package_base, version, repository, created) in (
                    select package_base, version, repository, max(created) from logs
                    where repository = :repository
                    group by package_base, version, repository
                  )
                )
                """,
                {
                    "repository": repository_id.id,
                }
            )

        def remove_older(connection: Connection) -> None:
            connection.execute(
                """
                delete from logs
                where (package_base, repository, process_id) in (
                  select package_base, repository, process_id from (
                    select package_base, repository, process_id, row_number() over (partition by package_base order by max(created) desc) as rn
                    from logs
                    where repository = :repository
                    group by package_base, repository, process_id
                  )
                  where rn > :offset
                )
                """,
                {
                    "offset": keep_last_records,
                    "repository": repository_id.id,
                }
            )

        def run(connection: Connection) -> None:
            remove_duplicates(connection)
            remove_older(connection)

        return self.with_connection(run, commit=True)
