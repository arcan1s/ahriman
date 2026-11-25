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
from ahriman.models.event import Event, EventType
from ahriman.models.repository_id import RepositoryId


class EventOperations(Operations):
    """
    operations for audit log table
    """

    def event_get(self, event: str | EventType | None = None, object_id: str | None = None,
                  from_date: int | float | None = None, to_date: int | float | None = None,
                  limit: int = -1, offset: int = 0, repository_id: RepositoryId | None = None) -> list[Event]:
        """
        get list of events with filters applied

        Args:
            event(str | EventType | None, optional): filter by event type (Default value = None)
            object_id(str | None, optional): filter by event object (Default value = None)
            from_date(int | float | None, optional): minimal creation date, inclusive (Default value = None)
            to_date(int | float | None, optional): maximal creation date, exclusive (Default value = None)
            limit(int, optional): limit records to the specified count, -1 means unlimited (Default value = -1)
            offset(int, optional): records offset (Default value = 0)
            repository_id(RepositoryId | None, optional): repository unique identifier override (Default value = None)

        Returns:
            list[Event]: list of audit log events
        """
        repository_id = repository_id or self._repository_id

        def run(connection: Connection) -> list[Event]:
            return [
                Event.from_json(row)
                for row in connection.execute(
                    """
                    select created, event, object_id, message, data from (
                        select * from auditlog
                        where (:event is null or event = :event)
                          and (:object_id is null or object_id = :object_id)
                          and (:from_date is null or created >= :from_date)
                          and (:to_date is null or created < :to_date)
                          and repository = :repository
                        order by created desc limit :limit offset :offset
                    ) order by created asc
                    """,
                    {
                        "event": event,
                        "object_id": object_id,
                        "repository": repository_id.id,
                        "from_date": from_date,
                        "to_date": to_date,
                        "limit": limit,
                        "offset": offset,
                    }
                )
            ]

        return self.with_connection(run)

    def event_insert(self, event: Event, repository_id: RepositoryId | None = None) -> None:
        """
        insert audit log event

        Args:
            event(Event): event to insert
            repository_id(RepositoryId | None, optional): repository unique identifier override (Default value = None)
        """
        repository_id = repository_id or self._repository_id

        def run(connection: Connection) -> None:
            connection.execute(
                """
                insert into auditlog
                (created, repository, event, object_id, message, data)
                values
                (:created, :repository, :event, :object_id, :message, :data)
                """,
                {
                    "created": event.created,
                    "repository": repository_id.id,
                    "event": event.event,
                    "object_id": event.object_id,
                    "message": event.message,
                    "data": event.data,
                })

        return self.with_connection(run, commit=True)

    def events_rotate(self, keep_last_records: int, repository_id: RepositoryId | None = None) -> None:
        """
        rotate events in storage, keeping only the last N records for each object

        Args:
            keep_last_records(int): number of last records to keep
            repository_id(RepositoryId | None, optional): repository unique identifier override (Default value = None)
        """
        repository_id = repository_id or self._repository_id

        def run(connection: Connection) -> None:
            connection.execute(
                """
                delete from auditlog
                where rowid in (
                  select rowid from (
                    select rowid, row_number() over (
                      partition by object_id order by created desc, rowid desc
                    ) as rn
                    from auditlog
                    where repository = :repository
                  )
                  where rn > :keep_last_records
                )
                """,
                {"keep_last_records": keep_last_records, "repository": repository_id.id},
            )

        self.with_connection(run, commit=True)
