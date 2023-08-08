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
import aiohttp_apispec  # type: ignore[import]

from aiohttp.web import HTTPNotFound, Response, json_response

from ahriman.models.user_access import UserAccess
from ahriman.web.schemas import AuthSchema, ErrorSchema, ProcessIdSchema, ProcessSchema
from ahriman.web.views.base import BaseView


class ProcessView(BaseView):
    """
    Process information web view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
    """

    GET_PERMISSION = UserAccess.Reporter

    @aiohttp_apispec.docs(
        tags=["Actions"],
        summary="Get process",
        description="Get process information",
        responses={
            200: {"description": "Success response", "schema": ProcessSchema},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            404: {"description": "Process ID is unknown", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [GET_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    @aiohttp_apispec.match_info_schema(ProcessIdSchema)
    async def get(self) -> Response:
        """
        get spawned process status

        Returns:
            Response: 200 with process information

        Raises:
            HTTPNotFound: if no process found
        """
        process_id = self.request.match_info["process_id"]

        is_alive = self.spawner.has_process(process_id)
        if not is_alive:
            raise HTTPNotFound(reason=f"No process {process_id} found")

        response = {
            "is_alive": is_alive,
        }

        return json_response(response)
