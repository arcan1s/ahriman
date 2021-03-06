#
# Copyright (c) 2021 ahriman team.
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

from ahriman.models.build_status import BuildStatusEnum
from ahriman.web.views.base import BaseView


class AhrimanView(BaseView):
    """
    service status web view
    """

    async def get(self) -> Response:
        """
        get current service status
        :return: 200 with service status object
        """
        return json_response(self.service.status.view())

    async def post(self) -> Response:
        """
        update service status

        JSON body must be supplied, the following model is used:
        {
            "status": "unknown",   # service status string, must be valid `BuildStatusEnum`
        }

        :return: 204 on success
        """
        data = await self.request.json()

        try:
            status = BuildStatusEnum(data["status"])
        except Exception as e:
            raise HTTPBadRequest(text=str(e))

        self.service.update_self(status)

        return HTTPNoContent()
