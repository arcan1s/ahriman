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
from aiohttp.web_exceptions import HTTPNotFound

from ahriman.core.exceptions import UnknownPackageError
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


class LogsView(BaseView):
    """
    package logs web view

    Attributes:
        DELETE_PERMISSION(UserAccess): (class attribute) delete permissions of self
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        HEAD_PERMISSION(UserAccess): (class attribute) head permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    DELETE_PERMISSION = POST_PERMISSION = UserAccess.Full
    GET_PERMISSION = HEAD_PERMISSION = UserAccess.Reporter

    async def delete(self) -> None:
        """
        delete package logs

        Raises:
            HTTPNoContent: on success response

        Examples:
            Example of command by using curl::

                $ curl -v -XDELETE 'http://example.com/api/v1/packages/ahriman/logs'
                > DELETE /api/v1/packages/ahriman/logs HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: */*
                >
                < HTTP/1.1 204 No Content
                < Date: Wed, 23 Nov 2022 19:26:40 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
        """
        package_base = self.request.match_info["package"]
        self.service.remove_logs(package_base, None)

        raise HTTPNoContent()

    async def get(self) -> Response:
        """
        get last package logs

        Returns:
            Response: 200 with package logs on success

        Examples:
            Example of command by using curl::

                $ curl -v -H 'Accept: application/json' 'http://example.com/api/v1/packages/ahriman/logs'
                > GET /api/v1/packages/ahriman/logs HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: application/json
                >
                < HTTP/1.1 200 OK
                < Content-Type: application/json; charset=utf-8
                < Content-Length: 100112
                < Date: Wed, 23 Nov 2022 19:24:14 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
                {"package_base": "ahriman", "status": {"status": "success", "timestamp": 1669231136}, "logs": "[2022-11-23 19:17:32] clone remote https://aur.archlinux.org/ahriman.git to /tmp/tmpy9j6fq9p using branch master"}
        """
        package_base = self.request.match_info["package"]

        try:
            _, status = self.service.get(package_base)
        except UnknownPackageError:
            raise HTTPNotFound()
        logs = self.service.get_logs(package_base)

        response = {
            "package_base": package_base,
            "status": status.view(),
            "logs": logs
        }
        return json_response(response)

    async def post(self) -> None:
        """
        create new package log record

        JSON body must be supplied, the following model is used::

            {
                "created": 42.001,           # log record created timestamp
                "message": "log message",    # log record
                "process_id": 42             # process id from which log record was emitted
            }

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNoContent: in case of success response

        Examples:
            Example of command by using curl::

                $ curl -v -H 'Content-Type: application/json' 'http://example.com/api/v1/packages/ahriman/logs' -d '{"created": 1669231764.042444, "message": "my log message", "process_id": 1}'
                > POST /api/v1/packages/ahriman/logs HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: */*
                > Content-Type: application/json
                > Content-Length: 76
                >
                < HTTP/1.1 204 No Content
                < Date: Wed, 23 Nov 2022 19:30:45 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
        """
        package_base = self.request.match_info["package"]
        data = await self.extract_data()

        try:
            created = data["created"]
            record = data["message"]
            process_id = data["process_id"]
        except Exception as e:
            raise HTTPBadRequest(reason=str(e))

        self.service.update_logs(LogRecordId(package_base, process_id), created, record)

        raise HTTPNoContent()
