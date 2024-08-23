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
import aiohttp_apispec  # type: ignore[import-untyped]

from aiohttp.web import HTTPBadRequest, HTTPNoContent, Response, json_response

from ahriman.models.event import Event
from ahriman.models.user_access import UserAccess
from ahriman.web.schemas import AuthSchema, ErrorSchema, EventSchema, EventSearchSchema
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

    @aiohttp_apispec.docs(
        tags=["Audit log"],
        summary="Get events",
        description="Retrieve events from audit log",
        responses={
            200: {"description": "Success response", "schema": EventSchema(many=True)},
            400: {"description": "Bad data is supplied", "schema": ErrorSchema},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [GET_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    @aiohttp_apispec.querystring_schema(EventSearchSchema)
    async def get(self) -> Response:
        """
        get events list

        Returns:
            Response: 200 with workers list on success
        """
        limit, offset = self.page()
        event = self.request.query.get("event") or None
        object_id = self.request.query.get("object_id") or None

        events = self.service().event_get(event, object_id, limit, offset)
        response = [event.view() for event in events]

        return json_response(response)

    @aiohttp_apispec.docs(
        tags=["Audit log"],
        summary="Create event",
        description="Add new event to the audit log",
        responses={
            204: {"description": "Success response"},
            400: {"description": "Bad data is supplied", "schema": ErrorSchema},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [POST_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    @aiohttp_apispec.json_schema(EventSchema)
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
