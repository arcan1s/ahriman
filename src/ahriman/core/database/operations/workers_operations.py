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
from ahriman.models.worker import Worker


class WorkersOperations(Operations):
    """
    operations for remote workers
    """

    def workers_get(self) -> list[Worker]:
        """
        retrieve registered workers

        Returns:
            list[Worker]: list of available workers
        """
        def run(connection: Connection) -> list[Worker]:
            return [
                Worker(row["address"], identifier=row["identifier"])
                for row in connection.execute("""select * from workers""")
            ]

        return self.with_connection(run)

    def workers_insert(self, worker: Worker) -> None:
        """
        insert or update worker in database

        Args:
            worker(Worker): remote worker descriptor
        """
        def run(connection: Connection) -> None:
            connection.execute(
                """
                insert into workers
                (identifier, address)
                values
                (:identifier, :address)
                on conflict (identifier) do update set
                address = :address
                """,
                worker.view()
            )

        return self.with_connection(run, commit=True)

    def workers_remove(self, identifier: str | None = None) -> None:
        """
        unregister remote worker

        Args:
            identifier(str | None, optional): remote worker identifier. If none set it will clear all workers
                (Default value = None)
        """
        def run(connection: Connection) -> None:
            connection.execute(
                """
                delete from workers where (:identifier is null or identifier = :identifier)
                """,
                {"identifier": identifier})

        return self.with_connection(run, commit=True)
