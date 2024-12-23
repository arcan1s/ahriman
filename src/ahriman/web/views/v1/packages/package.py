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
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.user_access import UserAccess
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import PackageNameSchema, PackageStatusSchema, PackageStatusSimplifiedSchema, \
    RepositoryIdSchema
from ahriman.web.views.base import BaseView
from ahriman.web.views.status_view_guard import StatusViewGuard


class PackageView(StatusViewGuard, BaseView):
    """
    package base specific web view

    Attributes:
        DELETE_PERMISSION(UserAccess): (class attribute) delete permissions of self
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    DELETE_PERMISSION = POST_PERMISSION = UserAccess.Full
    GET_PERMISSION = UserAccess.Read
    ROUTES = ["/api/v1/packages/{package}"]

    @apidocs(
        tags=["Packages"],
        summary="Delete package",
        description="Delete package and its status from service",
        permission=DELETE_PERMISSION,
        error_404_description="Repository is unknown",
        match_schema=PackageNameSchema,
        query_schema=RepositoryIdSchema,
    )
    async def delete(self) -> None:
        """
        delete package base from status page

        Raises:
            HTTPNoContent: on success response
        """
        package_base = self.request.match_info["package"]
        self.service().package_remove(package_base)

        raise HTTPNoContent

    @apidocs(
        tags=["Packages"],
        summary="Get package",
        description="Retrieve packages and its descriptor",
        permission=GET_PERMISSION,
        error_404_description="Package base and/or repository are unknown",
        schema=PackageStatusSchema(many=True),
        match_schema=PackageNameSchema,
        query_schema=RepositoryIdSchema,
    )
    async def get(self) -> Response:
        """
        get current package base status

        Returns:
            Response: 200 with package description on success

        Raises:
            HTTPNotFound: if no package was found
        """
        package_base = self.request.match_info["package"]
        repository_id = self.repository_id()

        try:
            package, status = self.service(repository_id).package_get(package_base)
        except UnknownPackageError:
            raise HTTPNotFound(reason=f"Package {package_base} is unknown")

        response = [
            {
                "package": package.view(),
                "status": status.view(),
                "repository": repository_id.view(),
            }
        ]
        return json_response(response)

    @apidocs(
        tags=["Packages"],
        summary="Update package",
        description="Update package status and set its descriptior optionally",
        permission=POST_PERMISSION,
        error_400_enabled=True,
        error_404_description="Repository is unknown",
        match_schema=PackageNameSchema,
        query_schema=RepositoryIdSchema,
        body_schema=PackageStatusSimplifiedSchema,
    )
    async def post(self) -> None:
        """
        update package build status

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNoContent: in case of success response
        """
        package_base = self.request.match_info["package"]

        try:
            data = await self.request.json()
            package = Package.from_json(data["package"]) if "package" in data else None
            status = BuildStatusEnum(data["status"])
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        try:
            if package is None:
                self.service().package_status_update(package_base, status)
            else:
                self.service().package_update(package, status)
        except UnknownPackageError:
            raise HTTPBadRequest(reason=f"Package {package_base} is unknown, but no package body set")

        raise HTTPNoContent
