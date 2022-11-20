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
    GET_PERMISSION = HEAD_PERMISSION = UserAccess.Read

    async def delete(self) -> None:
        """
        delete package logs

        Raises:
            HTTPNoContent: on success response
        """
        package_base = self.request.match_info["package"]
        self.service.remove_logs(package_base, None)

        raise HTTPNoContent()

    async def get(self) -> Response:
        """
        get last package logs

        Returns:
            Response: 200 with package logs on success
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
