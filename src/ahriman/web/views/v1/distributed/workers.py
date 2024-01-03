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

from collections.abc import Callable
from aiohttp.web import HTTPBadRequest, HTTPNoContent, Response, json_response

from ahriman.models.user_access import UserAccess
from ahriman.models.worker import Worker
from ahriman.web.schemas import AuthSchema, ErrorSchema, WorkerSchema
from ahriman.web.views.base import BaseView


class WorkersView(BaseView):
    """
    distributed workers view

    Attributes:
        DELETE_PERMISSION(UserAccess): (class attribute) delete permissions of self
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    DELETE_PERMISSION = GET_PERMISSION = POST_PERMISSION = UserAccess.Full
    ROUTES = ["/api/v1/distributed"]

    @aiohttp_apispec.docs(
        tags=["Distributed"],
        summary="Unregister all workers",
        description="Unregister and remove all known workers from the service",
        responses={
            204: {"description": "Success response"},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [DELETE_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    async def delete(self) -> None:
        """
        unregister worker

        Raises:
            HTTPNoContent: on success response
        """
        self.workers.workers_remove()

        raise HTTPNoContent

    @aiohttp_apispec.docs(
        tags=["Distributed"],
        summary="Get workers",
        description="Retrieve registered workers",
        responses={
            200: {"description": "Success response", "schema": WorkerSchema(many=True)},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [GET_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    async def get(self) -> Response:
        """
        get workers list

        Returns:
            Response: 200 with workers list on success
        """
        workers = self.workers.workers

        comparator: Callable[[Worker], str] = lambda item: item.identifier
        response = [worker.view() for worker in sorted(workers, key=comparator)]

        return json_response(response)

    @aiohttp_apispec.docs(
        tags=["Distributed"],
        summary="Register worker",
        description="Register or update remote worker",
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
    @aiohttp_apispec.json_schema(WorkerSchema)
    async def post(self) -> None:
        """
        register remote worker

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNoContent: in case of success response
        """
        try:
            data = await self.request.json()
            worker = Worker(data["address"], identifier=data["identifier"])
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        self.workers.workers_update(worker)

        raise HTTPNoContent
