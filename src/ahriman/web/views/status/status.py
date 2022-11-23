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

from ahriman import version
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.counters import Counters
from ahriman.models.internal_status import InternalStatus
from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


class StatusView(BaseView):
    """
    web service status web view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        HEAD_PERMISSION(UserAccess): (class attribute) head permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    GET_PERMISSION = HEAD_PERMISSION = UserAccess.Read
    POST_PERMISSION = UserAccess.Full

    async def get(self) -> Response:
        """
        get current service status

        Returns:
            Response: 200 with service status object

        Examples:
            Example of command by using curl::

                $ curl -v -H 'Accept: application/json' 'http://example.com/api/v1/status'
                > GET /api/v1/status HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: application/json
                >
                < HTTP/1.1 200 OK
                < Content-Type: application/json; charset=utf-8
                < Content-Length: 222
                < Date: Wed, 23 Nov 2022 19:32:31 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
                {"status": {"status": "success", "timestamp": 1669231237}, "architecture": "x86_64", "packages": {"total": 4, "unknown": 0, "pending": 0, "building": 0, "failed": 0, "success": 4}, "repository": "repo", "version": "2.3.0"}
        """
        counters = Counters.from_packages(self.service.packages)
        status = InternalStatus(
            status=self.service.status,
            architecture=self.service.architecture,
            packages=counters,
            repository=self.service.repository.name,
            version=version.__version__)

        return json_response(status.view())

    async def post(self) -> None:
        """
        update service status

        JSON body must be supplied, the following model is used::

            {
                "status": "unknown",   # service status string, must be valid ``BuildStatusEnum``
            }

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNoContent: in case of success response

        Examples:
            Example of command by using curl::

                $ curl -v -H 'Content-Type: application/json' 'http://example.com/api/v1/status' -d '{"status": "success"}'
                > POST /api/v1/status HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: */*
                > Content-Type: application/json
                > Content-Length: 21
                >
                < HTTP/1.1 204 No Content
                < Date: Wed, 23 Nov 2022 19:33:57 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
        """
        try:
            data = await self.extract_data()
            status = BuildStatusEnum(data["status"])
        except Exception as e:
            raise HTTPBadRequest(reason=str(e))

        self.service.update_self(status)

        raise HTTPNoContent()
