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
from aiohttp.web import HTTPBadRequest, HTTPNoContent, Response, json_response
from typing import ClassVar

from ahriman.models.dependencies import Dependencies
from ahriman.models.user_access import UserAccess
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import DependenciesSchema, PackageNameSchema, RepositoryIdSchema
from ahriman.web.views.base import BaseView
from ahriman.web.views.status_view_guard import StatusViewGuard


class DependenciesView(StatusViewGuard, BaseView):
    """
    package dependencies web view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    GET_PERMISSION: ClassVar[UserAccess] = UserAccess.Reporter
    POST_PERMISSION: ClassVar[UserAccess] = UserAccess.Full
    ROUTES = ["/api/v1/packages/{package}/dependencies"]

    @apidocs(
        tags=["Packages"],
        summary="Get package dependencies",
        description="Retrieve package implicit dependencies",
        permission=GET_PERMISSION,
        error_404_description="Package base and/or repository are unknown",
        schema=DependenciesSchema,
        match_schema=PackageNameSchema,
        query_schema=RepositoryIdSchema,
    )
    async def get(self) -> Response:
        """
        get package dependencies

        Returns:
            Response: 200 with package implicit dependencies on success

        Raises:
            HTTPNotFound: if package base is unknown
        """
        package_base = self.request.match_info["package"]

        dependencies = self.service(package_base=package_base).package_dependencies_get(package_base)

        return json_response(dependencies.view())

    @apidocs(
        tags=["Packages"],
        summary="Update package dependencies",
        description="Set package implicit dependencies",
        permission=POST_PERMISSION,
        error_400_enabled=True,
        error_404_description="Repository is unknown",
        match_schema=PackageNameSchema,
        query_schema=RepositoryIdSchema,
        body_schema=DependenciesSchema,
    )
    async def post(self) -> None:
        """
        insert new package dependencies

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNoContent: in case of success response
        """
        package_base = self.request.match_info["package"]

        try:
            data = await self.request.json()
            data["package_base"] = package_base  # read from path instead of object
            dependencies = Dependencies.from_json(data)
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        self.service(package_base=package_base).package_dependencies_update(package_base, dependencies)

        raise HTTPNoContent
