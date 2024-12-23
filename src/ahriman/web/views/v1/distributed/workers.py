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
from collections.abc import Callable

from ahriman.models.user_access import UserAccess
from ahriman.models.worker import Worker
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import WorkerSchema
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

    @apidocs(
        tags=["Distributed"],
        summary="Unregister all workers",
        description="Unregister and remove all known workers from the service",
        permission=DELETE_PERMISSION,
    )
    async def delete(self) -> None:
        """
        unregister worker

        Raises:
            HTTPNoContent: on success response
        """
        self.workers.workers_remove()

        raise HTTPNoContent

    @apidocs(
        tags=["Distributed"],
        summary="Get workers",
        description="Retrieve registered workers",
        permission=GET_PERMISSION,
        schema=WorkerSchema(many=True),
    )
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

    @apidocs(
        tags=["Distributed"],
        summary="Register worker",
        description="Register or update remote worker",
        permission=POST_PERMISSION,
        error_400_enabled=True,
        body_schema=WorkerSchema,
    )
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
