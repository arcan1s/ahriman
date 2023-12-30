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
import aiohttp_apispec  # type: ignore[import-untyped]

from aiohttp.web import HTTPNoContent, HTTPNotFound, Response, json_response

from ahriman.models.user_access import UserAccess
from ahriman.web.schemas import AuthSchema, ErrorSchema, WorkerIdSchema, WorkerSchema
from ahriman.web.views.base import BaseView


class WorkerView(BaseView):
    """
    distributed worker view

    Attributes:
        DELETE_PERMISSION(UserAccess): (class attribute) delete permissions of self
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
    """

    DELETE_PERMISSION = GET_PERMISSION = UserAccess.Full
    ROUTES = ["/api/v1/distributed/{identifier}"]

    @aiohttp_apispec.docs(
        tags=["Distributed"],
        summary="Unregister worker",
        description="Unregister worker and remove it from the service",
        responses={
            204: {"description": "Success response"},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [DELETE_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    @aiohttp_apispec.match_info_schema(WorkerIdSchema)
    async def delete(self) -> None:
        """
        unregister worker

        Raises:
            HTTPNoContent: on success response
        """
        identifier = self.request.match_info["identifier"]
        self.service().workers_remove(identifier)

        raise HTTPNoContent

    @aiohttp_apispec.docs(
        tags=["Distributed"],
        summary="Get worker",
        description="Retrieve registered worker by its identifier",
        responses={
            200: {"description": "Success response", "schema": WorkerSchema(many=True)},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            404: {"description": "Worker is unknown", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [GET_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    @aiohttp_apispec.match_info_schema(WorkerIdSchema)
    async def get(self) -> Response:
        """
        get worker by identifier

        Returns:
            Response: 200 with workers list on success

        Raises:
            HTTPNotFound: if no worker was found
        """
        identifier = self.request.match_info["identifier"]

        try:
            worker = next(worker for worker in self.service().workers_get() if worker.identifier == identifier)
        except StopIteration:
            raise HTTPNotFound(reason=f"Worker {identifier} not found")

        return json_response([worker.view()])
