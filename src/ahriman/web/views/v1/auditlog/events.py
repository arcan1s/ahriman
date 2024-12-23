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
from aiohttp.web import HTTPBadRequest, HTTPNoContent, Response, json_response

from ahriman.models.event import Event
from ahriman.models.user_access import UserAccess
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import EventSchema, EventSearchSchema
from ahriman.web.views.base import BaseView


class EventsView(BaseView):
    """
    audit log view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    GET_PERMISSION = POST_PERMISSION = UserAccess.Full
    ROUTES = ["/api/v1/events"]

    @apidocs(
        tags=["Audit log"],
        summary="Get events",
        description="Retrieve events from audit log",
        permission=GET_PERMISSION,
        error_400_enabled=True,
        schema=EventSchema(many=True),
        query_schema=EventSearchSchema,
    )
    async def get(self) -> Response:
        """
        get events list

        Returns:
            Response: 200 with workers list on success
        """
        limit, offset = self.page()
        event = self.request.query.get("event") or None
        object_id = self.request.query.get("object_id") or None
        try:
            from_date = to_date = None
            if (value := self.request.query.get("from_date")) is not None:
                from_date = int(value)
            if (value := self.request.query.get("to_date")) is not None:
                to_date = int(value)
        except ValueError as ex:
            raise HTTPBadRequest(reason=str(ex))

        events = self.service().event_get(event, object_id, from_date, to_date, limit, offset)
        response = [event.view() for event in events]

        return json_response(response)

    @apidocs(
        tags=["Audit log"],
        summary="Create event",
        description="Add new event to the audit log",
        permission=POST_PERMISSION,
        error_400_enabled=True,
        body_schema=EventSchema,
    )
    async def post(self) -> None:
        """
        add new audit log event

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNoContent: in case of success response
        """
        try:
            data = await self.request.json()
            event = Event.from_json(data)
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        self.service().event_add(event)

        raise HTTPNoContent
