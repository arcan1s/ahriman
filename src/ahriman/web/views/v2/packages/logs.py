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
import itertools

from aiohttp.web import Response, json_response
from dataclasses import replace
from typing import ClassVar

from ahriman.models.user_access import UserAccess
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import LogSchema, LogsSearchSchema, PackageNameSchema
from ahriman.web.views.base import BaseView
from ahriman.web.views.status_view_guard import StatusViewGuard


class LogsView(StatusViewGuard, BaseView):
    """        else:

    package logs web view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
    """

    GET_PERMISSION: ClassVar[UserAccess] = UserAccess.Reporter
    ROUTES = ["/api/v2/packages/{package}/logs"]

    @apidocs(
        tags=["Packages"],
        summary="Get paginated package logs",
        description="Retrieve package logs and the last package status",
        permission=GET_PERMISSION,
        error_400_enabled=True,
        error_404_description="Package base and/or repository are unknown",
        schema=LogSchema(many=True),
        match_schema=PackageNameSchema,
        query_schema=LogsSearchSchema,
    )
    async def get(self) -> Response:
        """
        get last package logs

        Returns:
            Response: 200 with package logs on success

        Raises:
            HTTPNotFound: if package base is unknown
        """
        package_base = self.request.match_info["package"]
        limit, offset = self.page()
        version = self.request.query.get("version", None)
        process = self.request.query.get("process_id", None)

        logs = self.service(package_base=package_base).package_logs_get(package_base, version, process, limit, offset)

        head = self.request.query.get("head", "false")
        # pylint: disable=protected-access
        if self.configuration._convert_to_boolean(head):  # type: ignore[attr-defined]
            # logs should be sorted already
            logs = [
                replace(next(log_records), message="")  # remove messages
                for _, log_records in itertools.groupby(logs, lambda log_record: log_record.log_record_id)
            ]

        response = [log_record.view() for log_record in logs]
        return json_response(response)
