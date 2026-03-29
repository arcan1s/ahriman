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
import json

from aiohttp.web import StreamResponse
from aiohttp_sse import EventSourceResponse, sse_response
from asyncio import Queue, QueueShutDown, wait_for
from typing import ClassVar

from ahriman.core.status.event_bus import SSEvent
from ahriman.models.event import EventType
from ahriman.models.user_access import UserAccess
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import EventBusFilterSchema, SSESchema
from ahriman.web.views.base import BaseView


class EventBusView(BaseView):
    """
    event bus SSE view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
    """

    GET_PERMISSION: ClassVar[UserAccess] = UserAccess.Full
    ROUTES = ["/api/v1/events/stream"]

    @staticmethod
    async def _run(response: EventSourceResponse, queue: Queue[SSEvent | None]) -> None:
        """
        read events from queue and send them to the client

        Args:
            response(EventSourceResponse): SSE response instance
            queue(Queue[SSEvent | None]): subscriber queue
        """
        while response.is_connected():
            try:
                message = await wait_for(queue.get(), timeout=response.ping_interval)
            except TimeoutError:
                continue

            if message is None:
                break  # terminate queue on sentinel event
            event_type, data = message

            await response.send(json.dumps(data), event=event_type)

    @apidocs(
        tags=["Audit log"],
        summary="Live updates",
        description="Stream live updates via SSE",
        permission=GET_PERMISSION,
        error_404_description="Repository is unknown",
        schema=SSESchema(many=True),
        query_schema=EventBusFilterSchema,
    )
    async def get(self) -> StreamResponse:
        """
        subscribe on updates

        Returns:
            StreamResponse: 200 with streaming updates
        """
        topics = [EventType(event) for event in self.request.query.getall("event", [])] or None
        event_bus = self.service().event_bus

        async with sse_response(self.request) as response:
            subscription_id, queue = await event_bus.subscribe(topics)

            try:
                await self._run(response, queue)
            except (ConnectionResetError, QueueShutDown):
                pass
            finally:
                await event_bus.unsubscribe(subscription_id)

        return response
