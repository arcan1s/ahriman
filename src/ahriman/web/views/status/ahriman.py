#
# Copyright (c) 2021-2022 ahriman team.
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
from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


class AhrimanView(BaseView):
    """
    service status web view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        HEAD_PERMISSION(UserAccess): (class attribute) head permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    GET_PERMISSION = HEAD_PERMISSION = UserAccess.Read
    POST_PERMISSION = UserAccess.Write

    async def get(self) -> Response:
        """
        get current service status

        Returns:
            Response: 200 with service status object
        """
        return json_response(self.service.status.view())

    async def post(self) -> None:
        """
        update service status

        JSON body must be supplied, the following model is used:

        >>> {
        >>>     "status": "unknown",   # service status string, must be valid `BuildStatusEnum`
        >>> }

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNoContent: in case of success response
        """
        try:
            data = await self.extract_data()
            status = BuildStatusEnum(data["status"])
        except Exception as e:
            raise HTTPBadRequest(reason=str(e))

        self.service.update_self(status)

        raise HTTPNoContent()
