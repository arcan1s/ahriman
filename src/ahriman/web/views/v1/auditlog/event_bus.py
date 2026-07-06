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

from aiohttp.web import HTTPBadRequest, Request, Response, StreamResponse
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
        READ_EVENTS(set[EventType]): (class attribute) events which are allowed for read-only users
    """

    READ_EVENTS: ClassVar[set[EventType]] = {
        EventType.PackageHeld,
        EventType.PackageOutdated,
        EventType.PackageRemoved,
        EventType.PackageStatusChanged,
        EventType.PackageUpdateFailed,
        EventType.PackageUpdated,
        EventType.ServiceStatusChanged,
    }
    ROUTES = ["/api/v1/events/stream"]

    @classmethod
    async def get_permission(cls, request: Request) -> UserAccess:
        """
        retrieve user permission from the request

        Args:
            request(Request): request object

        Returns:
            UserAccess: extracted permission
        """
        if request.method.upper() not in ("GET", "HEAD"):
            return await BaseView.get_permission(request)

        permission = UserAccess.Full
        try:
            topics = cls(request)._topics()
        except HTTPBadRequest:
            topics = None

        if topics is not None and set(topics).issubset(cls.READ_EVENTS):
            permission = UserAccess.Read

        return permission

    @staticmethod
    async def _run(response: EventSourceResponse, queue: Queue[SSEvent]) -> None:
        """
        read events from queue and send them to the client

        Args:
            response(EventSourceResponse): SSE response instance
            queue(Queue[SSEvent]): subscriber queue
        """
        while response.is_connected():
            try:
                event_type, data = await wait_for(queue.get(), timeout=response.ping_interval)
            except TimeoutError:
                continue
            except QueueShutDown:
                break

            await response.send(json.dumps(data), event=event_type)

    def _topics(self) -> list[EventType] | None:
        """
        parse event filter from request query

        Returns:
            list[EventType] | None: event filter if any

        Raises:
            HTTPBadRequest: if invalid event type is supplied
        """
        if self.request.query is None:
            return None

        try:
            return [EventType(event) for event in self.request.query.getall("event", [])] or None
        except ValueError as ex:
            raise HTTPBadRequest(reason=str(ex))

    @apidocs(
        tags=["Audit log"],
        summary="Live updates",
        description="Stream live updates via SSE. Read-only users may subscribe only when all requested event filters "
                    "belong to read-safe package and service status events; build log or unfiltered streams require "
                    "full access. Streams are live-only and do not replay missed events after reconnect.",
        permission=UserAccess.Full,
        error_400_enabled=True,
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
        topics = self._topics()
        object_id = self.request.query.get("object_id")
        event_bus = self.service().event_bus

        async with sse_response(self.request) as response:
            subscription_id, queue = await event_bus.subscribe(topics, object_id=object_id)

            try:
                await self._run(response, queue)
            except (ConnectionResetError, QueueShutDown):
                pass
            finally:
                await event_bus.unsubscribe(subscription_id)

        return response

    async def head(self) -> StreamResponse:
        """
        HEAD method implementation based on the result of GET method

        Returns:
            StreamResponse: generated response for the request
        """
        self._topics()
        self.service()

        return Response(headers={
            "Cache-Control": "no-cache",
            "Content-Type": "text/event-stream",
        })
