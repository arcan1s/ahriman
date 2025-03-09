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
from aiohttp.web import HTTPNotFound, Response, json_response
from typing import ClassVar

from ahriman.models.user_access import UserAccess
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import ProcessIdSchema, ProcessSchema
from ahriman.web.views.base import BaseView


class ProcessView(BaseView):
    """
    Process information web view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
    """

    GET_PERMISSION: ClassVar[UserAccess] = UserAccess.Reporter
    ROUTES = ["/api/v1/service/process/{process_id}"]

    @apidocs(
        tags=["Actions"],
        summary="Get process",
        description="Get process information",
        permission=GET_PERMISSION,
        error_404_description="Process is unknown",
        schema=ProcessSchema,
        match_schema=ProcessIdSchema,
    )
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
