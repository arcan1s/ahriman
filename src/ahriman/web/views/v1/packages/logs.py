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
from aiohttp.web import HTTPBadRequest, HTTPNoContent, HTTPNotFound, Response, json_response

from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.utils import pretty_datetime
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.user_access import UserAccess
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import LogsSchema, PackageNameSchema, PackageVersionSchema, RepositoryIdSchema, \
    VersionedLogSchema
from ahriman.web.views.base import BaseView
from ahriman.web.views.status_view_guard import StatusViewGuard


class LogsView(StatusViewGuard, BaseView):
    """
    package logs web view

    Attributes:
        DELETE_PERMISSION(UserAccess): (class attribute) delete permissions of self
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    DELETE_PERMISSION = POST_PERMISSION = UserAccess.Full
    GET_PERMISSION = UserAccess.Reporter
    ROUTES = ["/api/v1/packages/{package}/logs"]

    @apidocs(
        tags=["Packages"],
        summary="Delete package logs",
        description="Delete all logs which belong to the specified package",
        permission=DELETE_PERMISSION,
        error_404_description="Repository is unknown",
        match_schema=PackageNameSchema,
        query_schema=PackageVersionSchema,
    )
    async def delete(self) -> None:
        """
        delete package logs

        Raises:
            HTTPNoContent: on success response
        """
        package_base = self.request.match_info["package"]
        version = self.request.query.get("version")
        self.service().package_logs_remove(package_base, version)

        raise HTTPNoContent

    @apidocs(
        tags=["Packages"],
        summary="Get package logs",
        description="Retrieve all package logs and the last package status",
        permission=GET_PERMISSION,
        error_404_description="Package base and/or repository are unknown",
        schema=LogsSchema,
        match_schema=PackageNameSchema,
        query_schema=RepositoryIdSchema,
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

        try:
            _, status = self.service().package_get(package_base)
            logs = self.service(package_base=package_base).package_logs_get(package_base, -1, 0)
        except UnknownPackageError:
            raise HTTPNotFound(reason=f"Package {package_base} is unknown")

        response = {
            "package_base": package_base,
            "status": status.view(),
            "logs": "\n".join(f"[{pretty_datetime(created)}] {message}" for created, message in logs)
        }
        return json_response(response)

    @apidocs(
        tags=["Packages"],
        summary="Add package logs",
        description="Insert new package log record",
        permission=POST_PERMISSION,
        error_400_enabled=True,
        error_404_description="Repository is unknown",
        match_schema=PackageNameSchema,
        body_schema=VersionedLogSchema,
    )
    async def post(self) -> None:
        """
        create new package log record

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNoContent: in case of success response
        """
        package_base = self.request.match_info["package"]

        try:
            data = await self.request.json()
            created = data["created"]
            record = data["message"]
            version = data["version"]
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        self.service().package_logs_add(LogRecordId(package_base, version), created, record)

        raise HTTPNoContent
