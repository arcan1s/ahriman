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
import uuid

from asyncio import Lock, Queue, QueueFull
from typing import Any

from ahriman.core.log import LazyLogging
from ahriman.models.event import EventType


SSEvent = tuple[str, dict[str, Any]]


class EventBus(LazyLogging):
    """
    event bus implementation

    Attributes:
        max_size(int): maximum size of queue
    """

    def __init__(self, max_size: int) -> None:
        """
        Args:
            max_size(int): maximum size of queue
        """
        self.max_size = max_size

        self._lock = Lock()
        self._subscribers: dict[str, tuple[list[EventType] | None, Queue[SSEvent | None]]] = {}

    async def broadcast(self, event_type: EventType, object_id: str | None, **kwargs: Any) -> None:
        """
        broadcast event to all subscribers

        Args:
            event_type(EventType): event type
            object_id(str | None): object identifier (e.g. package base)
            **kwargs(Any): additional event data
        """
        event: dict[str, Any] = {"object_id": object_id}
        event.update(kwargs)

        async with self._lock:
            for subscriber_id, (topics, queue) in self._subscribers.items():
                if topics is not None and event_type not in topics:
                    continue
                try:
                    queue.put_nowait((event_type, event))
                except QueueFull:
                    self.logger.warning("discard message to slow subscriber %s", subscriber_id)

    async def shutdown(self) -> None:
        """
        gracefully shutdown all subscribers
        """
        async with self._lock:
            for _, queue in self._subscribers.values():
                try:
                    queue.put_nowait(None)
                except QueueFull:
                    pass
                queue.shutdown()

    async def subscribe(self, topics: list[EventType] | None = None) -> tuple[str, Queue[SSEvent | None]]:
        """
        register new subscriber

        Args:
            topics(list[EventType] | None, optional): list of event types to filter by. If ``None`` is set,
                all events will be delivered (Default value = None)

        Returns:
            tuple[str, Queue[SSEvent | None]]: subscriber identifier and associated queue
        """
        subscriber_id = str(uuid.uuid4())
        queue: Queue[SSEvent | None] = Queue(self.max_size)

        async with self._lock:
            self._subscribers[subscriber_id] = (topics, queue)

        return subscriber_id, queue

    async def unsubscribe(self, subscriber_id: str) -> None:
        """
        unsubscribe from events

        Args:
            subscriber_id(str): subscriber unique identifier
        """
        async with self._lock:
            result = self._subscribers.pop(subscriber_id, None)
        if result is not None:
            _, queue = result
            queue.shutdown()
