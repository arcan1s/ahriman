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
from sqlite3 import Connection
from typing import List, Optional

from ahriman.core.database.operations import Operations
from ahriman.models.log_record_id import LogRecordId


class LogsOperations(Operations):
    """
    logs operations
    """

    def logs_get(self, package_base: str) -> str:
        """
        extract logs for specified package base

        Args:
            package_base(str): package base to extract logs

        Return:
            str: full package log
        """
        def run(connection: Connection) -> List[str]:
            return [
                row["record"]
                for row in connection.execute(
                    """
                    select record from logs where package_base = :package_base
                    order by created asc
                    """,
                    {"package_base": package_base})
            ]

        records = self.with_connection(run)
        return "\n".join(records)

    def logs_insert(self, log_record_id: LogRecordId, created: float, record: str) -> None:
        """
        write new log record to database

        Args:
            log_record_id(LogRecordId): current log record id
            created(float): log created timestamp from log record attribute
            record(str): log record
        """
        def run(connection: Connection) -> None:
            connection.execute(
                """
                insert into logs
                (package_base, process_id, created, record)
                values
                (:package_base, :process_id, :created, :record)
                """,
                dict(
                    package_base=log_record_id.package_base,
                    process_id=log_record_id.process_id,
                    created=created,
                    record=record
                )
            )

        return self.with_connection(run, commit=True)

    def logs_remove(self, package_base: str, current_process_id: Optional[int]) -> None:
        """
        remove log records for the specified package

        Args:
            package_base(str): package base to remove logs
            current_process_id(Optional[int]): current process id. If set it will remove only logs belonging to another
                process
        """
        def run(connection: Connection) -> None:
            connection.execute(
                """
                delete from logs
                where package_base = :package_base and (:process_id is null or process_id <> :process_id)
                """,
                {"package_base": package_base, "process_id": current_process_id}
            )

        return self.with_connection(run, commit=True)
