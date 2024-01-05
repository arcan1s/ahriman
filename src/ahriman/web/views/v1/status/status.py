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

from ahriman import __version__
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.counters import Counters
from ahriman.models.internal_status import InternalStatus
from ahriman.models.user_access import UserAccess
from ahriman.web.schemas import AuthSchema, ErrorSchema, InternalStatusSchema, RepositoryIdSchema, StatusSchema
from ahriman.web.views.base import BaseView
from ahriman.web.views.status_view_guard import StatusViewGuard


class StatusView(StatusViewGuard, BaseView):
    """
    web service status web view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    GET_PERMISSION = UserAccess.Read
    POST_PERMISSION = UserAccess.Full
    ROUTES = ["/api/v1/status"]

    @aiohttp_apispec.docs(
        tags=["Status"],
        summary="Web service status",
        description="Get web service status counters",
        responses={
            200: {"description": "Success response", "schema": InternalStatusSchema},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            404: {"description": "Repository is unknown", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [GET_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    async def get(self) -> Response:
        """
        get current service status

        Returns:
            Response: 200 with service status object
        """
        repository_id = self.repository_id()
        counters = Counters.from_packages(self.service(repository_id).packages)
        status = InternalStatus(
            status=self.service(repository_id).status,
            architecture=repository_id.architecture,
            packages=counters,
            repository=repository_id.name,
            version=__version__,
        )

        return json_response(status.view())

    @aiohttp_apispec.docs(
        tags=["Status"],
        summary="Set web service status",
        description="Update web service status. Counters will remain unchanged",
        responses={
            204: {"description": "Success response"},
            400: {"description": "Bad data is supplied", "schema": ErrorSchema},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            404: {"description": "Repository is unknown", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [POST_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    @aiohttp_apispec.querystring_schema(RepositoryIdSchema)
    @aiohttp_apispec.json_schema(StatusSchema)
    async def post(self) -> None:
        """
        update service status

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNoContent: in case of success response
        """
        try:
            data = await self.request.json()
            status = BuildStatusEnum(data["status"])
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        self.service().status_update(status)

        raise HTTPNoContent
